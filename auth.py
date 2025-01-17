from base64 import urlsafe_b64encode
from datetime import datetime
from hashlib import sha256
from json import dump
from json import load
from os.path import exists
from secrets import token_urlsafe
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
import webbrowser

from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session


class FitbitOAuth2:
    """
    Handles OAuth2 PKCE authentication flow for Fitbit API with token caching
    """

    AUTH_URL: str = "https://www.fitbit.com/oauth2/authorize"
    TOKEN_URL: str = "https://api.fitbit.com/oauth2/token"
    TOKEN_FILE: str = "tokens.json"

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
        scope: Optional[List[str]] = None,
        token_file: Optional[str] = None,
    ) -> None:
        """
        Initialize Fitbit OAuth2 PKCE flow

        Parameters:
            client_id: Your Fitbit client ID from dev.fitbit.com
            client_secret: Your Fitbit client secret
            redirect_uri: Your registered redirect URI
            scope: List of Fitbit scopes to request
            token_file: Optional custom path for token file
        """
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.redirect_uri: str = redirect_uri
        self.scope: List[str] = scope or self.DEFAULT_SCOPES
        self.token_file: str = token_file or self.TOKEN_FILE

        # Generate PKCE code verifier and challenge
        self.code_verifier: str = token_urlsafe(64)
        self.code_challenge: str = self._generate_code_challenge()

        # Try to load existing tokens
        self.token: Optional[Dict[str, Any]] = self._load_token()

        # Initialize OAuth session with any existing token
        self.oauth: OAuth2Session = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            token=self.token,
            auto_refresh_url=self.TOKEN_URL,
            auto_refresh_kwargs={"client_id": self.client_id, "client_secret": self.client_secret},
            token_updater=self._save_token,
        )

    def _generate_code_challenge(self) -> str:
        """Generate PKCE code challenge from verifier using SHA-256"""
        challenge: bytes = sha256(self.code_verifier.encode("utf-8")).digest()
        return urlsafe_b64encode(challenge).decode("utf-8").rstrip("=")

    def _load_token(self) -> Optional[Dict[str, Any]]:
        """Load token from file if it exists and is valid"""
        try:
            if exists(self.token_file):
                with open(self.token_file, "r") as f:
                    token: Dict[str, Any] = load(f)

                # Check if token is expired or will expire soon
                expires_at: float = token.get("expires_at", 0)
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
        with open(self.token_file, "w") as f:
            dump(token, f)
        self.token = token

    def is_authenticated(self) -> bool:
        """Check if we have valid tokens"""
        if not self.token:
            return False
        expires_at: float = self.token.get("expires_at", 0)
        return expires_at > datetime.now().timestamp()

    def authenticate(self, force_new: bool = False) -> bool:
        """
        Complete authentication flow if needed

        Parameters:
            force_new: Force new authentication even if valid token exists

        Returns:
            True if authenticated successfully
        """
        if not force_new and self.is_authenticated():
            return True

        # Get authorization URL and open it in browser
        auth_url: str
        state: str
        auth_url, state = self.get_authorization_url()
        print(f"Opening browser to: {auth_url}")
        webbrowser.open(auth_url)

        # Get callback URL from user
        callback_url: str = input("Enter the full callback URL you were redirected to: ")

        # Exchange authorization code for token
        token: Dict[str, Any] = self.fetch_token(callback_url)
        self._save_token(token)
        return True

    def get_authorization_url(self) -> Tuple[str, str]:
        """Get the Fitbit authorization URL"""
        return self.oauth.authorization_url(
            self.AUTH_URL, code_challenge=self.code_challenge, code_challenge_method="S256"
        )

    def fetch_token(self, authorization_response: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        auth: HTTPBasicAuth = HTTPBasicAuth(self.client_id, self.client_secret)
        return self.oauth.fetch_token(
            self.TOKEN_URL,
            authorization_response=authorization_response,
            code_verifier=self.code_verifier,
            auth=auth,
            include_client_id=True,
        )

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh the access token"""
        auth: HTTPBasicAuth = HTTPBasicAuth(self.client_id, self.client_secret)
        extra: Dict[str, str] = {
            "client_id": self.client_id,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        token: Dict[str, Any] = self.oauth.refresh_token(self.TOKEN_URL, auth=auth, **extra)
        self._save_token(token)
        return token
