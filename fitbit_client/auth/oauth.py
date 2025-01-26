# fitbit_client/auth/oauth.py

# Standard library imports
from base64 import urlsafe_b64encode
from datetime import datetime
from hashlib import sha256
from json import dump
from json import load
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


class FitbitOAuth2:
    """Handles OAuth2 PKCE authentication flow for Fitbit API"""

    AUTH_URL: str = "https://www.fitbit.com/oauth2/authorize"
    TOKEN_URL: str = "https://api.fitbit.com/oauth2/token"
    TOKEN_FILE: str = "/tmp/tokens.json"

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
        use_callback_server: bool = True,
    ) -> None:
        self.logger = getLogger("fitbit_client.oauth")
        self.logger.debug("Initializing OAuth2 client")

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.use_callback_server = use_callback_server

        environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        self.logger.debug("OAUTHLIB_INSECURE_TRANSPORT set to 1")

        # Initialize callback server if needed
        self.callback_server = None
        if use_callback_server:
            self.logger.debug("Initializing callback server")
            self.callback_server = CallbackServer(redirect_uri)

        # Generate PKCE code verifier and challenge
        self.code_verifier = token_urlsafe(64)
        self.code_challenge = self._generate_code_challenge()
        self.logger.debug("Generated PKCE code verifier and challenge")

        # Try to load existing tokens
        self.token = self._load_token()

        # Initialize OAuth session
        self.logger.debug("Initializing OAuth session")
        self.oauth = OAuth2Session(
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
        self.logger.debug("Generating PKCE code challenge")
        challenge = sha256(self.code_verifier.encode("utf-8")).digest()
        return urlsafe_b64encode(challenge).decode("utf-8").rstrip("=")

    def _load_token(self) -> Optional[Dict[str, Any]]:
        """Load token from file if it exists and is valid"""
        try:
            if exists(self.TOKEN_FILE):
                self.logger.debug(f"Loading token from {self.TOKEN_FILE}")
                with open(self.TOKEN_FILE, "r") as f:
                    token = load(f)

                # Check if token is expired or will expire soon
                expires_at = token.get("expires_at", 0)
                if expires_at > datetime.now().timestamp() + 300:  # 5 min buffer
                    self.logger.debug("Loaded valid token from file")
                    return token

                self.logger.info("Token expired or will expire soon")

                # Try to refresh if expired
                if token.get("refresh_token"):
                    try:
                        self.logger.debug("Attempting to refresh expired token")
                        return self.refresh_token(token["refresh_token"])
                    except Exception as e:
                        self.logger.error(f"Failed to refresh token: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error loading token: {str(e)}")
        return None

    def _save_token(self, token: Dict[str, Any]) -> None:
        """Save token to file"""
        try:
            self.logger.debug(f"Saving token to {self.TOKEN_FILE}")
            with open(self.TOKEN_FILE, "w") as f:
                dump(token, f)
            self.token = token
            self.logger.debug("Token saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save token: {str(e)}")

    def authenticate(self, force_new: bool = False) -> bool:
        """
        Complete authentication flow if needed

        Args:
            force_new: Force new authentication even if valid token exists

        Returns:
            bool: True if authenticated successfully
        """
        if not force_new and self.is_authenticated():
            self.logger.debug("Using existing valid authentication")
            return True

        # Get authorization URL and open it in browser
        auth_url, state = self.get_authorization_url()
        self.logger.info(f"Starting OAuth flow, opening browser to: {auth_url}")
        browser_open(auth_url)

        if self.use_callback_server and self.callback_server:
            # Start server and wait for callback
            self.logger.debug("Starting callback server")
            self.callback_server.start()
            callback_url = self.callback_server.wait_for_callback()
            if not callback_url:
                self.logger.error("Timeout waiting for OAuth callback")
                raise RuntimeError("Timeout waiting for OAuth callback")
            self.callback_server.stop()
            self.logger.debug("Callback server stopped")
        else:
            # Get callback URL from user
            self.logger.info("Waiting for manual callback URL entry")
            callback_url = input("Enter the full callback URL you were redirected to: ")

        # Exchange authorization code for token
        self.logger.debug("Exchanging authorization code for token")
        token = self.fetch_token(callback_url)
        self._save_token(token)
        self.logger.info("OAuth flow completed successfully")

        return True

    def is_authenticated(self) -> bool:
        """Check if we have valid tokens"""
        if not self.token:
            self.logger.debug("No token present")
            return False
        expires_at = self.token.get("expires_at", 0)
        is_valid = expires_at > datetime.now().timestamp()
        self.logger.debug(f"Token validity check: {is_valid}")
        return is_valid

    def get_authorization_url(self) -> Tuple[str, str]:
        """Get the Fitbit authorization URL"""
        self.logger.debug("Generating authorization URL")
        return self.oauth.authorization_url(
            self.AUTH_URL, code_challenge=self.code_challenge, code_challenge_method="S256"
        )

    def fetch_token(self, authorization_response: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        self.logger.debug("Fetching token with authorization response")
        auth = HTTPBasicAuth(self.client_id, self.client_secret)
        return self.oauth.fetch_token(
            self.TOKEN_URL,
            authorization_response=authorization_response,
            code_verifier=self.code_verifier,
            auth=auth,
            include_client_id=True,
        )

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh the access token"""
        self.logger.debug("Attempting to refresh token")
        auth = HTTPBasicAuth(self.client_id, self.client_secret)
        extra = {
            "client_id": self.client_id,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        token = self.oauth.refresh_token(self.TOKEN_URL, auth=auth, **extra)
        self._save_token(token)
        self.logger.debug("Token refreshed successfully")
        return token
