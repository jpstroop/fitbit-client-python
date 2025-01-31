# tests/auth/test_oauth.py

# Standard library imports
from json import dump
from tempfile import NamedTemporaryFile
from time import time
from unittest.mock import patch

# Third party imports
from pytest import fixture
from requests.auth import HTTPBasicAuth

# Local imports
from fitbit_client.auth.oauth import FitbitOAuth2


class TestFitbitOAuth2:
    @fixture
    def oauth(self):
        """Create a FitbitOAuth2 instance with test configuration"""
        with NamedTemporaryFile() as temp_token_file:
            oauth = FitbitOAuth2(
                client_id="test_client_id",
                client_secret="test_client_secret",
                redirect_uri="https://localhost:8080",
                token_cache_path=temp_token_file.name,
                use_callback_server=False,
            )
            yield oauth

    def test_pkce_challenge_generation(self, oauth):
        """Test PKCE code challenge generation"""
        assert len(oauth.code_verifier) >= 43
        assert len(oauth.code_challenge) >= 43
        assert "=" not in oauth.code_challenge

        new_challenge = oauth._generate_code_challenge()
        assert new_challenge == oauth.code_challenge

    def test_token_management(self, oauth):
        """Test token saving and loading"""
        test_token = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_at": time() + 3600,
        }

        oauth._save_token(test_token)
        loaded_token = oauth._load_token()

        assert loaded_token["access_token"] == test_token["access_token"]
        assert loaded_token["refresh_token"] == test_token["refresh_token"]

    def test_token_expiration(self, oauth):
        """Test handling of expired tokens"""
        expired_token = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_at": time() - 3600,
        }

        with open(oauth.token_cache_path, "w") as f:
            dump(expired_token, f)

        with patch.object(oauth, "refresh_token") as mock_refresh:
            mock_refresh.return_value = {
                "access_token": "new_access_token",
                "expires_at": time() + 3600,
            }

            loaded_token = oauth._load_token()
            assert loaded_token["access_token"] == "new_access_token"

    def test_authentication_status(self, oauth):
        """Test authentication status checking"""
        oauth.token = None
        assert not oauth.is_authenticated()

        oauth.token = {"expires_at": time() + 3600}
        assert oauth.is_authenticated()

        oauth.token = {"expires_at": time() - 3600}
        assert not oauth.is_authenticated()

    def test_token_refresh(self, oauth):
        """Test token refresh functionality"""
        with patch.object(oauth.session, "refresh_token") as mock_refresh:
            mock_refresh.return_value = {
                "access_token": "refreshed_token",
                "expires_at": time() + 3600,
            }

            refreshed = oauth.refresh_token("old_refresh_token")

            assert mock_refresh.called
            assert isinstance(mock_refresh.call_args[1]["auth"], HTTPBasicAuth)
            assert refreshed["access_token"] == "refreshed_token"
            assert oauth.token == refreshed
