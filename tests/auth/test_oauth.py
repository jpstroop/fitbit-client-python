# tests/auth/test_oauth.py

# Standard library imports
from json import dumps
from time import time
from unittest.mock import Mock
from unittest.mock import mock_open
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.auth.oauth import FitbitOAuth2
from fitbit_client.exceptions import ExpiredTokenException
from fitbit_client.exceptions import InvalidClientException
from fitbit_client.exceptions import InvalidGrantException
from fitbit_client.exceptions import InvalidRequestException
from fitbit_client.exceptions import InvalidTokenException


class TestFitbitOAuth2:
    @fixture
    def oauth(self):
        """Create FitbitOAuth2 instance with minimal setup"""
        with (
            patch("fitbit_client.auth.oauth.CallbackServer"),
            patch("fitbit_client.auth.oauth.OAuth2Session"),
        ):
            return FitbitOAuth2(
                client_id="test_id",
                client_secret="test_secret",
                redirect_uri="https://localhost:8080",
                token_cache_path="/tmp/test_token.json",
                use_callback_server=False,
            )

    def test_initialization(self):
        """Test successful initialization"""
        with (
            patch("fitbit_client.auth.oauth.CallbackServer"),
            patch("fitbit_client.auth.oauth.OAuth2Session"),
        ):
            oauth = FitbitOAuth2(
                client_id="test_id",
                client_secret="test_secret",
                redirect_uri="https://localhost:8080",
                token_cache_path="/tmp/test_token.json",
            )
            assert oauth.client_id == "test_id"
            assert oauth.client_secret == "test_secret"
            assert oauth.redirect_uri == "https://localhost:8080"

    def test_https_required(self):
        """Test that non-HTTPS redirect URIs are rejected"""
        with (
            patch("fitbit_client.auth.oauth.CallbackServer"),
            patch("fitbit_client.auth.oauth.OAuth2Session"),
            raises(InvalidRequestException) as exc_info,
        ):
            FitbitOAuth2(
                client_id="test_id",
                client_secret="test_secret",
                redirect_uri="http://localhost:8080",
                token_cache_path="/tmp/test_token.json",
            )

        assert "should use https protocol" in str(exc_info.value)
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "request"

    def test_code_verifier_length_validation(self, oauth):
        """Test PKCE code verifier length validation"""
        # Save original valid verifier
        valid_verifier = oauth.code_verifier

        # Test with short verifier
        oauth.code_verifier = "x" * 42  # Too short
        with raises(InvalidRequestException) as exc_info:
            oauth._generate_code_challenge()
        assert "length must be between 43 and 128" in str(exc_info.value)
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "invalid_request"

        # Test with long verifier
        oauth.code_verifier = "x" * 129  # Too long
        with raises(InvalidRequestException) as exc_info:
            oauth._generate_code_challenge()
        assert "length must be between 43 and 128" in str(exc_info.value)

        # Test valid length
        oauth.code_verifier = "x" * 64
        challenge = oauth._generate_code_challenge()
        assert challenge  # Should return a non-empty string

        # Restore valid verifier
        oauth.code_verifier = valid_verifier

    def test_authenticate_success(self, oauth):
        """Test successful authentication flow"""
        mock_auth_response = "https://localhost:8080/callback?code=test_code&state=test_state"
        mock_token = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "expires_at": time() + 3600,
        }

        oauth.get_authorization_url = Mock(return_value=("test_url", "test_state"))
        oauth.fetch_token = Mock(return_value=mock_token)

        with patch("builtins.input", return_value=mock_auth_response), patch("webbrowser.open"):
            assert oauth.authenticate() is True

    def test_refresh_token_expired(self, oauth):
        """Test handling of expired refresh token"""
        mock_session = Mock()
        mock_session.refresh_token.side_effect = Exception("expired_token")
        oauth.session = mock_session

        with raises(ExpiredTokenException) as exc_info:
            oauth.refresh_token("old_token")
        assert "Access token expired" in str(exc_info.value)
        assert exc_info.value.status_code == 401
        assert exc_info.value.error_type == "expired_token"

    def test_refresh_token_invalid(self, oauth):
        """Test handling of invalid refresh token"""
        mock_session = Mock()
        mock_session.refresh_token.side_effect = Exception("invalid_grant")
        oauth.session = mock_session

        with raises(InvalidGrantException) as exc_info:
            oauth.refresh_token("bad_token")
        assert "Refresh token invalid" in str(exc_info.value)
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "invalid_grant"

    def test_fetch_token_invalid_client(self, oauth):
        """Test handling of invalid client credentials"""
        mock_session = Mock()
        mock_session.fetch_token.side_effect = Exception("invalid_client")
        oauth.session = mock_session

        with raises(InvalidClientException) as exc_info:
            oauth.fetch_token("callback_url")
        assert "Invalid client credentials" in str(exc_info.value)
        assert exc_info.value.status_code == 401
        assert exc_info.value.error_type == "invalid_client"

    def test_fetch_token_invalid_token(self, oauth):
        """Test handling of invalid authorization code"""
        mock_session = Mock()
        mock_session.fetch_token.side_effect = Exception("invalid_token")
        oauth.session = mock_session

        with raises(InvalidTokenException) as exc_info:
            oauth.fetch_token("callback_url")
        assert "Invalid authorization code" in str(exc_info.value)
        assert exc_info.value.status_code == 401
        assert exc_info.value.error_type == "invalid_token"

    def test_load_token_missing_file(self, oauth):
        """Test handling of missing token cache file"""
        with patch("fitbit_client.auth.oauth.exists", return_value=False):
            token = oauth._load_token()
            assert token is None

    def test_load_token_invalid_json(self, oauth):
        """Test handling of corrupted token cache file"""
        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data="invalid json")),
        ):
            token = oauth._load_token()
            assert token is None

    def test_load_token_expired_with_refresh(self, oauth):
        """Test loading expired token with valid refresh token"""
        expired_token = {
            "access_token": "old_token",
            "refresh_token": "refresh_token",
            "expires_at": time() - 3600,
        }
        new_token = {"access_token": "new_token", "expires_at": time() + 3600}

        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=dumps(expired_token))),
            patch.object(oauth, "refresh_token", return_value=new_token),
        ):
            token = oauth._load_token()
            assert token == new_token

    def test_load_token_expired_refresh_fails(self, oauth):
        """Test loading expired token when refresh fails"""
        expired_token = {
            "access_token": "old_token",
            "refresh_token": "refresh_token",
            "expires_at": time() - 3600,
        }

        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=dumps(expired_token))),
            patch.object(
                oauth,
                "refresh_token",
                side_effect=InvalidGrantException(
                    message="Refresh token invalid", status_code=400, error_type="invalid_grant"
                ),
            ),
        ):
            token = oauth._load_token()
            assert token is None

    def test_save_token(self, oauth):
        """Test token saving"""
        mock_token = {"access_token": "test_token"}

        # Simulate the entire JSON serialization process
        with (
            patch("fitbit_client.auth.oauth.open", mock_open()) as mock_file,
            patch("json.dump") as mock_json_dump,
        ):
            oauth._save_token(mock_token)

            # Verify file was opened correctly
            mock_file.assert_called_once_with(oauth.token_cache_path, "w")

            # Verify JSON dump was called with correct arguments
            mock_json_dump.assert_called_once_with(mock_token, mock_file())
