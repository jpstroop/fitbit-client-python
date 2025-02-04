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
from typing import Any
from typing import Dict
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
from fitbit_client.exceptions import ExpiredTokenException
from fitbit_client.exceptions import InvalidClientException
from fitbit_client.exceptions import InvalidGrantException
from fitbit_client.exceptions import InvalidRequestException
from fitbit_client.exceptions import InvalidTokenException


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
                error_type="request",
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

    def _load_token(self) -> Optional[Dict[str, Any]]:
        """Load token from file if it exists and is valid"""
        try:
            if exists(self.token_cache_path):
                with open(self.token_cache_path, "r") as f:
                    token = json.load(f)

                expires_at = token.get("expires_at", 0)
                if expires_at > datetime.now().timestamp() + 300:  # 5 min buffer
                    return token

                if token.get("refresh_token"):
                    try:
                        return self.refresh_token(token["refresh_token"])
                    except InvalidGrantException:
                        # Invalid/expired refresh token
                        return None
        except Exception:
            return None
        return None

    def _save_token(self, token: Dict[str, Any]) -> None:
        """Save token to file"""
        with open(self.token_cache_path, "w") as f:
            json.dump(token, f)
        self.token = token

    def authenticate(self, force_new: bool = False) -> bool:
        """Complete authentication flow if needed"""
        if not force_new and self.is_authenticated():
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
        try:
            token = self.fetch_token(callback_url)
            self._save_token(token)
            return True
        except Exception as e:
            if "invalid_grant" in str(e):
                raise InvalidGrantException(
                    message="Authorization code expired or invalid",
                    status_code=400,
                    error_type="invalid_grant",
                ) from e
            raise

    def is_authenticated(self) -> bool:
        """Check if we have valid tokens"""
        if not self.token:
            return False
        expires_at = self.token.get("expires_at", 0)
        return expires_at > datetime.now().timestamp()

    def get_authorization_url(self) -> Tuple[str, str]:
        """Get the Fitbit authorization URL"""
        return self.session.authorization_url(
            self.AUTH_URL, code_challenge=self.code_challenge, code_challenge_method="S256"
        )

    def fetch_token(self, authorization_response: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            auth = HTTPBasicAuth(self.client_id, self.client_secret)
            return self.session.fetch_token(
                self.TOKEN_URL,
                authorization_response=authorization_response,
                code_verifier=self.code_verifier,
                auth=auth,
                include_client_id=True,
            )
        except Exception as e:
            error_msg = str(e).lower()
            logger = getLogger("fitbit_client.oauth")

            if "invalid_client" in error_msg:
                logger.error(
                    f"InvalidClientException: Authentication failed "
                    f"(Client ID: {self.client_id[:4]}..., Error: {str(e)})"
                )
                raise InvalidClientException(
                    message="Invalid client credentials",
                    status_code=401,
                    error_type="invalid_client",
                ) from e
            if "invalid_token" in error_msg:
                logger.error(
                    f"InvalidTokenException: Token validation failed " f"(Error: {str(e)})"
                )
                raise InvalidTokenException(
                    message="Invalid authorization code",
                    status_code=401,
                    error_type="invalid_token",
                ) from e

            logger.error(f"OAuthException: {e.__class__.__name__}: {str(e)}")
            raise

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh the access token"""
        try:
            auth = HTTPBasicAuth(self.client_id, self.client_secret)
            extra = {
                "client_id": self.client_id,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            }

            token = self.session.refresh_token(self.TOKEN_URL, auth=auth, **extra)
            self._save_token(token)
            return token
        except Exception as e:
            error_msg = str(e).lower()
            if "expired_token" in error_msg:
                raise ExpiredTokenException(
                    message="Access token expired", status_code=401, error_type="expired_token"
                ) from e
            if "invalid_grant" in error_msg:
                raise InvalidGrantException(
                    message="Refresh token invalid", status_code=400, error_type="invalid_grant"
                ) from e
            raise
