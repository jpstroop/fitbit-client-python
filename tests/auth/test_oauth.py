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

    # Initialization Tests
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

    # PKCE Tests
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

    def test_authorization_url_generation(self, oauth):
        """Test generation of authorization URL with PKCE parameters"""
        mock_session = Mock()
        mock_session.authorization_url.return_value = ("https://test.url", "test_state")
        oauth.session = mock_session

        url, state = oauth.get_authorization_url()

        assert url == "https://test.url"
        assert state == "test_state"
        mock_session.authorization_url.assert_called_once_with(
            oauth.AUTH_URL, code_challenge=oauth.code_challenge, code_challenge_method="S256"
        )

    # Authentication Tests
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

    def test_authenticate_with_callback_server(self, oauth):
        """Test authentication using callback server"""
        mock_auth_response = "https://localhost:8080/callback?code=test_code&state=test_state"
        mock_token = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "expires_at": time() + 3600,
        }

        callback_server = Mock()
        callback_server.wait_for_callback.return_value = mock_auth_response
        oauth.callback_server = callback_server
        oauth.use_callback_server = True

        oauth.get_authorization_url = Mock(return_value=("test_url", "test_state"))
        oauth.fetch_token = Mock(return_value=mock_token)
        oauth.is_authenticated = Mock(return_value=False)

        with patch("webbrowser.open"):
            assert oauth.authenticate() is True
            callback_server.start.assert_called_once()
            callback_server.wait_for_callback.assert_called_once()
            callback_server.stop.assert_called_once()

    def test_authenticate_callback_timeout(self, oauth):
        """Test authentication when callback server times out"""
        callback_server = Mock()
        callback_server.wait_for_callback.return_value = None
        oauth.callback_server = callback_server
        oauth.use_callback_server = True

        oauth.get_authorization_url = Mock(return_value=("test_url", "test_state"))
        oauth.is_authenticated = Mock(return_value=False)

        with patch("webbrowser.open"):
            with raises(InvalidRequestException):
                oauth.authenticate()

    def test_authenticate_already_authenticated(self, oauth):
        """Test authenticate when already authenticated"""
        oauth.is_authenticated = Mock(return_value=True)
        oauth.get_authorization_url = Mock()
        oauth._save_token = Mock()
        oauth.fetch_token = Mock()

        assert oauth.authenticate() is True

        # Verify no other methods were called
        oauth.get_authorization_url.assert_not_called()
        oauth._save_token.assert_not_called()
        oauth.fetch_token.assert_not_called()

    def test_authenticate_force_new(self, oauth):
        """Test forcing new authentication even when already authenticated"""
        mock_auth_response = "https://localhost:8080/callback?code=test_code&state=test_state"
        mock_token = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "expires_at": time() + 3600,
        }

        # Setup mocks
        oauth.is_authenticated = Mock(return_value=True)
        oauth.get_authorization_url = Mock(return_value=("test_url", "test_state"))
        oauth.fetch_token = Mock(return_value=mock_token)
        oauth._save_token = Mock()

        with patch("builtins.input", return_value=mock_auth_response), patch("webbrowser.open"):
            result = oauth.authenticate(force_new=True)

        # Verify result and method calls
        assert result is True
        oauth.get_authorization_url.assert_called_once()
        oauth.fetch_token.assert_called_once_with(mock_auth_response)
        oauth._save_token.assert_called_once_with(mock_token)

    def test_authenticate_invalid_grant(self, oauth):
        """Test authentication failure due to invalid grant during token fetch"""
        mock_auth_response = "https://localhost:8080/callback?code=invalid_code&state=test_state"

        class MockException(Exception):
            def __str__(self):
                return "invalid_grant"

        oauth.get_authorization_url = Mock(return_value=("test_url", "test_state"))
        oauth.fetch_token = Mock(side_effect=MockException())
        oauth.is_authenticated = Mock(return_value=False)

        with (
            patch("builtins.input", return_value=mock_auth_response),
            patch("webbrowser.open"),
            raises(InvalidGrantException) as exc_info,
        ):
            oauth.authenticate()

        assert "Authorization code expired or invalid" in str(exc_info.value)
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "invalid_grant"

    def test_authenticate_unexpected_error(self, oauth):
        """Test authentication failure due to unexpected error during token fetch"""
        mock_auth_response = "https://localhost:8080/callback?code=test_code&state=test_state"
        original_error = RuntimeError("some unhandled error")

        oauth.get_authorization_url = Mock(return_value=("test_url", "test_state"))
        oauth.fetch_token = Mock(side_effect=original_error)
        oauth.is_authenticated = Mock(return_value=False)

        with (
            patch("builtins.input", return_value=mock_auth_response),
            patch("webbrowser.open"),
            raises(RuntimeError) as exc_info,
        ):
            oauth.authenticate()

        assert str(exc_info.value) == "some unhandled error"

    def test_authenticate_exception_flows(self, oauth):
        """Test exception handling paths in authenticate method"""
        mock_auth_response = "https://localhost:8080/callback?code=test_code&state=test_state"

        oauth.get_authorization_url = Mock(return_value=("test_url", "test_state"))
        oauth.is_authenticated = Mock(return_value=False)

        # Test invalid_grant flow
        oauth.fetch_token = Mock(side_effect=Exception("invalid_grant"))
        with (
            patch("builtins.input", return_value=mock_auth_response),
            patch("webbrowser.open"),
            raises(InvalidGrantException) as exc_info,
        ):
            oauth.authenticate()

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "invalid_grant"

        # Test other exception flow
        oauth.fetch_token = Mock(side_effect=ValueError("other error"))
        with (
            patch("builtins.input", return_value=mock_auth_response),
            patch("webbrowser.open"),
            raises(ValueError) as exc_info,
        ):
            oauth.authenticate()

        assert str(exc_info.value) == "other error"

    # Token Fetching Tests
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

    def test_fetch_token_unhandled_error_logging(self, oauth):
        """Test unhandled error logging in fetch_token method"""
        original_error = ValueError("Unhandled OAuth error")
        mock_session = Mock()
        mock_session.fetch_token.side_effect = original_error
        oauth.session = mock_session

        # Setup logger mock to capture log message
        mock_logger = Mock()
        oauth.logger = mock_logger

        with raises(ValueError) as exc_info:
            oauth.fetch_token("callback_url")

        # Verify the error was logged correctly
        assert str(exc_info.value) == "Unhandled OAuth error"
        mock_logger.error.assert_called_once()
        log_message = mock_logger.error.call_args[0][0]
        assert "OAuthException" in log_message
        assert "ValueError" in log_message
        assert "Unhandled OAuth error" in log_message

    # Token Refresh Tests
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

    def test_refresh_token_other_error(self, oauth):
        """Test handling of unexpected error during token refresh"""
        mock_session = Mock()
        unexpected_error = ValueError("unexpected error")
        mock_session.refresh_token.side_effect = unexpected_error
        oauth.session = mock_session

        with raises(ValueError) as exc_info:
            oauth.refresh_token("test_token")

        assert "unexpected error" in str(exc_info.value)

    def test_refresh_token_save_and_return(self, oauth):
        """Test that refresh_token saves and returns the new token"""
        mock_token = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_at": time() + 3600,
        }

        mock_session = Mock()
        mock_session.refresh_token.return_value = mock_token
        oauth.session = mock_session

        # Mock the _save_token method
        save_token_mock = Mock()
        oauth._save_token = save_token_mock

        # Call refresh_token
        result = oauth.refresh_token("old_refresh_token")

        # Verify _save_token was called with the new token
        save_token_mock.assert_called_once_with(mock_token)

        # Verify the new token was returned
        assert result == mock_token

    # Token Storage Tests
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

    def test_load_token_general_exception(self, oauth):
        """Test handling of general exception during token loading"""
        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", side_effect=Exception("file access error")),
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

    def test_load_token_with_refresh_token_exception_handling(self, oauth):
        """Test token loading with refresh token and exception handling"""
        expired_token = {
            "access_token": "expired_token",
            "refresh_token": "refresh_token",
            "expires_at": time() - 3600,  # 1 hour in the past
        }

        # Mock file operations to return the expired token
        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=dumps(expired_token))),
            patch("fitbit_client.auth.oauth.datetime") as mock_datetime,
        ):

            # Make sure the token is considered expired
            mock_datetime.now.return_value.timestamp.return_value = time()

            # Test with InvalidGrantException during refresh
            with patch.object(
                oauth,
                "refresh_token",
                side_effect=InvalidGrantException(
                    message="Refresh token invalid", status_code=400, error_type="invalid_grant"
                ),
            ):
                result = oauth._load_token()
                assert result is None

    def test_load_token_expired_without_refresh_token(self, oauth):
        """Test loading an expired token that doesn't have a refresh token"""
        # Create an expired token without a refresh_token field
        expired_token = {
            "access_token": "expired_token",
            "expires_at": time() - 3600,  # 1 hour in the past
        }

        # Mock file operations to return the expired token
        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=dumps(expired_token))),
            patch("fitbit_client.auth.oauth.datetime") as mock_datetime,
        ):

            # Make sure the token is considered expired
            mock_datetime.now.return_value.timestamp.return_value = time()

            # The refresh_token method should not be called
            refresh_mock = Mock()
            oauth.refresh_token = refresh_mock

            result = oauth._load_token()

            # Verify the result is None and refresh was not attempted
            assert result is None
            refresh_mock.assert_not_called()

    # Authentication Status Tests
    def test_is_authenticated_no_token(self, oauth):
        """Test is_authenticated when no token exists"""
        oauth.token = None
        assert not oauth.is_authenticated()

    def test_is_authenticated_with_valid_token(self, oauth):
        """Test is_authenticated with a non-expired token"""
        # Setup a valid token with future expiry
        future_time = time() + 3600  # 1 hour in the future
        oauth.token = {"access_token": "valid_token", "expires_at": future_time}

        # Use mock to ensure consistent datetime comparison
        with patch("fitbit_client.auth.oauth.datetime") as mock_datetime:
            mock_datetime.now.return_value.timestamp.return_value = time()
            assert oauth.is_authenticated() is True

    def test_is_authenticated_with_expired_token(self, oauth):
        """Test is_authenticated with an expired token"""
        # Setup an expired token
        past_time = time() - 3600  # 1 hour in the past
        oauth.token = {"access_token": "expired_token", "expires_at": past_time}

        # Use mock to ensure consistent datetime comparison
        with patch("fitbit_client.auth.oauth.datetime") as mock_datetime:
            mock_datetime.now.return_value.timestamp.return_value = time()
            assert oauth.is_authenticated() is False
