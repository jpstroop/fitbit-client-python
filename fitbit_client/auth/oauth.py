# fitbit_client/auth/oauth.py

# Standard library imports
from base64 import urlsafe_b64encode
from datetime import datetime
from hashlib import sha256
from json import dump
from json import load
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
    """Handles OAuth2 PKCE authentication flow for Fitbit API

    Note:
        This resource requires the 'social' scope.
        The Fitbit privacy setting 'My Friends' (Private, Friends Only or Public) determines
        the access to a user's list of friends.
        This scope does not provide access to friends' Fitbit data - those users need to
        individually consent to share their data.
    """

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
        """Initialize OAuth2 flow

        Args:
            client_id: Your Fitbit API client ID
            client_secret: Your Fitbit API client secret
            redirect_uri: Complete OAuth redirect URI (e.g. "https://localhost:8080")
            use_callback_server: Whether to use local callback server
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.use_callback_server = use_callback_server

        environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        # Initialize callback server if needed
        self.callback_server = None
        if use_callback_server:
            self.callback_server = CallbackServer(redirect_uri)

        # Generate PKCE code verifier and challenge
        self.code_verifier = token_urlsafe(64)
        self.code_challenge = self._generate_code_challenge()

        # Try to load existing tokens
        self.token = self._load_token()

        # Initialize OAuth session
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
        challenge = sha256(self.code_verifier.encode("utf-8")).digest()
        return urlsafe_b64encode(challenge).decode("utf-8").rstrip("=")

    def _load_token(self) -> Optional[Dict[str, Any]]:
        """Load token from file if it exists and is valid"""
        try:
            if exists(self.TOKEN_FILE):
                with open(self.TOKEN_FILE, "r") as f:
                    token = load(f)

                # Check if token is expired or will expire soon
                expires_at = token.get("expires_at", 0)
                if expires_at > datetime.now().timestamp() + 300:  # 5 min buffer
                    return token

                # Try to refresh if expired
                if token.get("refresh_token"):
                    try:
                        return self.refresh_token(token["refresh_token"])
                    except:
                        pass
        except Exception as e:
            print(f"Error loading token: {e}")
        return None

    def _save_token(self, token: Dict[str, Any]) -> None:
        """Save token to file"""
        with open(self.TOKEN_FILE, "w") as f:
            dump(token, f)
        self.token = token

    def authenticate(self, force_new: bool = False) -> bool:
        """
        Complete authentication flow if needed

        Args:
            force_new: Force new authentication even if valid token exists

        Returns:
            bool: True if authenticated successfully
        """
        if not force_new and self.is_authenticated():
            return True

        # Get authorization URL and open it in browser
        auth_url, state = self.get_authorization_url()
        print(f"Opening browser to: {auth_url}")
        browser_open(auth_url)

        if self.use_callback_server and self.callback_server:
            # Start server and wait for callback
            self.callback_server.start()
            callback_url = self.callback_server.wait_for_callback()
            if not callback_url:
                raise RuntimeError("Timeout waiting for OAuth callback")
            self.callback_server.stop()
        else:
            # Get callback URL from user
            callback_url = input("Enter the full callback URL you were redirected to: ")

        # Exchange authorization code for token
        token = self.fetch_token(callback_url)
        self._save_token(token)

        return True

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
        auth = HTTPBasicAuth(self.client_id, self.client_secret)
        return self.session.fetch_token(
            self.TOKEN_URL,
            authorization_response=authorization_response,
            code_verifier=self.code_verifier,
            auth=auth,
            include_client_id=True,
        )

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh the access token"""
        auth = HTTPBasicAuth(self.client_id, self.client_secret)
        extra = {
            "client_id": self.client_id,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        token = self.session.refresh_token(self.TOKEN_URL, auth=auth, **extra)
        self._save_token(token)
        return token
