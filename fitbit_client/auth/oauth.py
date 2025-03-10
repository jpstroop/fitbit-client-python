# fitbit_client/auth/oauth.py

# Standard library imports
from base64 import urlsafe_b64encode
from datetime import datetime
from hashlib import sha256
import json  # importing the whole module is the only way it can be patched in tests, apparently
from logging import getLogger
from os import environ
from os.path import exists
from secrets import token_urlsafe
from typing import List
from typing import Optional
from typing import Tuple
from urllib.parse import urlparse
from webbrowser import open as browser_open

# Third party imports
from requests.auth import HTTPBasicAuth
from requests_oauthlib.oauth2_session import OAuth2Session

# Local imports
from fitbit_client.auth.callback_server import CallbackServer
from fitbit_client.exceptions import InvalidGrantException
from fitbit_client.exceptions import InvalidRequestException
from fitbit_client.utils.types import TokenDict


class FitbitOAuth2:
    """Handles OAuth2 PKCE authentication flow for Fitbit API"""

    AUTH_URL: str = "https://www.fitbit.com/oauth2/authorize"
    TOKEN_URL: str = "https://api.fitbit.com/oauth2/token"

    DEFAULT_SCOPES: List[str] = [
        "activity",
        "cardio_fitness",
        "electrocardiogram",
        "heartrate",
        "irregular_rhythm_notifications",
        "location",
        "nutrition",
        "oxygen_saturation",
        "profile",
        "respiratory_rate",
        "settings",
        "sleep",
        "social",
        "temperature",
        "weight",
    ]

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        token_cache_path: str,
        use_callback_server: bool = True,
    ) -> None:
        self.logger = getLogger("fitbit_client.oauth")
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.use_callback_server = use_callback_server
        self.token_cache_path = token_cache_path

        parsed = urlparse(redirect_uri)
        if parsed.scheme != "https":
            raise InvalidRequestException(
                message="This request should use https protocol.",
                status_code=400,
                error_type="invalid_request",
                field_name="redirect_uri",
            )

        environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        self.callback_server = None
        if use_callback_server:
            self.callback_server = CallbackServer(redirect_uri)

        self.code_verifier = token_urlsafe(64)
        self.code_challenge = self._generate_code_challenge()

        self.token = self._load_token()

        self.session = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.DEFAULT_SCOPES,
            token=self.token,
            auto_refresh_url=self.TOKEN_URL,
            auto_refresh_kwargs={"client_id": self.client_id, "client_secret": self.client_secret},
            token_updater=self._save_token,
        )

    def _generate_code_challenge(self) -> str:
        """Generate PKCE code challenge from verifier using SHA-256"""
        if len(self.code_verifier) < 43 or len(self.code_verifier) > 128:
            raise InvalidRequestException(
                message="The code_verifier parameter length must be between 43 and 128",
                status_code=400,
                error_type="invalid_request",
            )

        challenge = sha256(self.code_verifier.encode("utf-8")).digest()
        return urlsafe_b64encode(challenge).decode("utf-8").rstrip("=")

    def _load_token(self) -> Optional[TokenDict]:
        """Load token from file if it exists and is valid"""
        try:
            if exists(self.token_cache_path):
                with open(self.token_cache_path, "r") as f:
                    token_data = json.load(f)
                    # Convert the loaded data to our TokenDict type
                    token: TokenDict = token_data

                expires_at = token.get("expires_at", 0)
                if expires_at > datetime.now().timestamp() + 300:  # 5 min buffer
                    return token

                if token.get("refresh_token"):
                    try:
                        return self.refresh_token(token["refresh_token"])
                    except InvalidGrantException:
                        # Invalid/expired refresh token
                        return None
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON in token cache file: {self.token_cache_path}")
            return None
        except OSError as e:
            self.logger.error(f"Error reading token cache file: {self.token_cache_path}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error loading token: {e.__class__.__name__}: {str(e)}")
            return None
        return None

    def _save_token(self, token: TokenDict) -> None:
        """Save token to file"""
        with open(self.token_cache_path, "w") as f:
            json.dump(token, f)
        self.token = token

    def authenticate(self, force_new: bool = False) -> bool:
        """Complete authentication flow if needed

        Args:
            force_new: Force new authentication even if valid token exists

        Returns:
            bool: True if authenticated successfully

        Raises:
            InvalidRequestException: If the request syntax is invalid
            InvalidClientException: If the client_id is invalid
            InvalidGrantException: If the grant_type is invalid
            InvalidTokenException: If the OAuth token is invalid
            ExpiredTokenException: If the OAuth token has expired
            OAuthException: Base class for all OAuth-related exceptions
            SystemException: If there's a system-level failure
        """
        if not force_new and self.is_authenticated():
            self.logger.debug("Authentication token exchange completed successfully")
            return True

        # Get authorization URL and open it in browser
        auth_url, state = self.get_authorization_url()
        browser_open(auth_url)

        if self.use_callback_server and self.callback_server:
            # Start server and wait for callback
            self.callback_server.start()
            callback_url = self.callback_server.wait_for_callback()
            if not callback_url:
                raise InvalidRequestException(
                    message="Timeout waiting for OAuth callback",
                    status_code=400,
                    error_type="invalid_request",
                )
            self.callback_server.stop()
        else:
            # Get callback URL from user
            callback_url = input("Enter the full callback URL: ")

        # Exchange authorization code for token
        token = self.fetch_token(callback_url)
        self._save_token(token)
        return True

    def is_authenticated(self) -> bool:
        """Check if we have valid tokens"""
        if not self.token:
            return False
        expires_at = self.token.get("expires_at", 0)
        return bool(expires_at > datetime.now().timestamp())

    def get_authorization_url(self) -> Tuple[str, str]:
        """Get the Fitbit authorization URL"""
        auth_url_tuple = self.session.authorization_url(
            self.AUTH_URL, code_challenge=self.code_challenge, code_challenge_method="S256"
        )
        return (str(auth_url_tuple[0]), str(auth_url_tuple[1]))

    def fetch_token(self, authorization_response: str) -> TokenDict:
        """Exchange authorization code for access token

        Args:
            authorization_response: The full callback URL with authorization code

        Returns:
            TokenDict: Dictionary containing access token and other OAuth details

        Raises:
            InvalidClientException: If the client credentials are invalid
            InvalidTokenException: If the authorization code is invalid
            InvalidGrantException: If the authorization grant is invalid
            ExpiredTokenException: If the token has expired
            OAuthException: For other OAuth-related errors
        """
        try:
            auth = HTTPBasicAuth(self.client_id, self.client_secret)
            token_data = self.session.fetch_token(
                self.TOKEN_URL,
                authorization_response=authorization_response,
                code_verifier=self.code_verifier,
                auth=auth,
                include_client_id=True,
            )
            # Convert to our typed dictionary
            token: TokenDict = token_data
            return token
        except Exception as e:
            error_msg = str(e).lower()

            # Use standard error mapping from ERROR_TYPE_EXCEPTIONS
            # Local imports
            from fitbit_client.exceptions import ERROR_TYPE_EXCEPTIONS
            from fitbit_client.exceptions import OAuthException

            # Check for known error types
            for error_type, exception_class in ERROR_TYPE_EXCEPTIONS.items():
                if error_type in error_msg:
                    # Special case for client ID to mask most of it in logs
                    if error_type == "invalid_client":
                        self.logger.error(
                            f"{exception_class.__name__}: Authentication failed "
                            f"(Client ID: {self.client_id[:4]}..., Error: {str(e)})"
                        )
                    else:
                        self.logger.error(
                            f"{exception_class.__name__}: {error_type} error during token fetch: {str(e)}"
                        )

                    raise exception_class(
                        message=str(e),
                        status_code=(
                            401 if "token" in error_type or error_type == "authorization" else 400
                        ),
                        error_type=error_type,
                    ) from e

            # If no specific error type found, use OAuthException
            self.logger.error(
                f"OAuthException during token fetch: {e.__class__.__name__}: {str(e)}"
            )
            raise OAuthException(message=str(e), status_code=400, error_type="oauth") from e

    def refresh_token(self, refresh_token: str) -> TokenDict:
        """Refresh the access token

        Args:
            refresh_token: The refresh token to use

        Returns:
            TokenDict: Dictionary containing new access token and other OAuth details

        Raises:
            ExpiredTokenException: If the access token has expired
            InvalidGrantException: If the refresh token is invalid
            InvalidClientException: If the client credentials are invalid
            OAuthException: For other OAuth-related errors
        """
        try:
            auth = HTTPBasicAuth(self.client_id, self.client_secret)
            extra = {
                "client_id": self.client_id,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            }

            token_data = self.session.refresh_token(self.TOKEN_URL, auth=auth, **extra)
            # Convert to our typed dictionary
            token: TokenDict = token_data
            self._save_token(token)
            return token
        except Exception as e:
            error_msg = str(e).lower()

            # Use standard error mapping from ERROR_TYPE_EXCEPTIONS
            # Local imports
            from fitbit_client.exceptions import ERROR_TYPE_EXCEPTIONS
            from fitbit_client.exceptions import OAuthException

            # Check for known error types
            for error_type, exception_class in ERROR_TYPE_EXCEPTIONS.items():
                if error_type in error_msg:
                    self.logger.error(
                        f"{exception_class.__name__}: {error_type} error during token refresh: {str(e)}"
                    )

                    raise exception_class(
                        message=str(e),
                        status_code=(
                            401 if "token" in error_type or error_type == "authorization" else 400
                        ),
                        error_type=error_type,
                    ) from e

            # If no specific error type found, use OAuthException
            self.logger.error(
                f"OAuthException during token refresh: {e.__class__.__name__}: {str(e)}"
            )
            raise OAuthException(message=str(e), status_code=400, error_type="oauth") from e
