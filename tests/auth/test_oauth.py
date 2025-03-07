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
        assert exc_info.value.error_type == "invalid_request"
        assert exc_info.value.field_name == "redirect_uri"

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

    def test_authenticate_uses_fetch_token_directly(self, oauth):
        """Test that authenticate passes callback URL directly to fetch_token"""
        mock_auth_response = "https://localhost:8080/callback?code=test_code&state=test_state"
        mock_token = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "expires_at": time() + 3600,
        }

        # Setup mocks
        oauth.get_authorization_url = Mock(return_value=("test_url", "test_state"))
        oauth.fetch_token = Mock(return_value=mock_token)
        oauth.is_authenticated = Mock(return_value=False)
        oauth._save_token = Mock()

        with patch("builtins.input", return_value=mock_auth_response), patch("webbrowser.open"):
            oauth.authenticate()

        # Verify fetch_token was called with the callback response
        oauth.fetch_token.assert_called_once_with(mock_auth_response)
        oauth._save_token.assert_called_once_with(mock_token)

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

    def test_fetch_token_handles_all_exception_types(self, oauth):
        """Test that fetch_token handles all exception types from ERROR_TYPE_EXCEPTIONS map"""
        # Local imports
        from fitbit_client.exceptions import ERROR_TYPE_EXCEPTIONS

        # Get a few key error types to test (no need to test all of them)
        test_error_types = [
            "expired_token",
            "invalid_grant",
            "invalid_client",
            "insufficient_scope",
        ]

        for error_type in test_error_types:
            # Create a mock error with this error type in the message
            mock_error = Exception(f"Error with {error_type} in the message")
            mock_session = Mock()
            mock_session.fetch_token.side_effect = mock_error
            oauth.session = mock_session

            # Get the expected exception class for this error type
            expected_exception = ERROR_TYPE_EXCEPTIONS[error_type]

            # Test that the correct exception is raised
            with raises(expected_exception) as exc_info:
                oauth.fetch_token("https://localhost:8080/callback?code=test")

            # Verify the exception has correct attributes
            assert exc_info.value.error_type == error_type
            assert exc_info.value.status_code in [400, 401]  # Depending on error type

    # Token Fetching Tests
    def test_fetch_token_returns_typed_dict(self, oauth):
        """Test that fetch_token correctly returns a properly typed TokenDict"""
        mock_token_data = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "expires_at": time() + 3600,
            "scope": ["activity", "profile"],
        }

        # Mock the session's fetch_token method to return our test data
        mock_session = Mock()
        mock_session.fetch_token.return_value = mock_token_data
        oauth.session = mock_session

        # Call the method we're testing
        result = oauth.fetch_token("https://localhost:8080/callback?code=test_code")

        # Verify the result matches our test data
        assert result == mock_token_data
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["access_token"] == "test_access_token"

        # Verify the session's fetch_token was called with correct parameters
        mock_session.fetch_token.assert_called_once()
        call_args = mock_session.fetch_token.call_args[0]
        call_kwargs = mock_session.fetch_token.call_args[1]
        assert call_args[0] == oauth.TOKEN_URL
        assert (
            call_kwargs["authorization_response"]
            == "https://localhost:8080/callback?code=test_code"
        )
        assert call_kwargs["code_verifier"] == oauth.code_verifier
        assert call_kwargs["include_client_id"] is True

    def test_fetch_token_invalid_client(self, oauth):
        """Test handling of invalid client credentials"""
        # Create a more realistic error message that matches what the API would return
        mock_session = Mock()
        mock_session.fetch_token.side_effect = Exception(
            "invalid_client: The client credentials are invalid"
        )
        oauth.session = mock_session

        with raises(InvalidClientException) as exc_info:
            oauth.fetch_token("callback_url")
        assert exc_info.value.status_code == 400  # Our implementation uses 400
        assert exc_info.value.error_type == "invalid_client"
        # The message from the API should be preserved in the exception
        assert "invalid_client" in str(exc_info.value)

    def test_fetch_token_invalid_token(self, oauth):
        """Test handling of invalid authorization code"""
        mock_session = Mock()
        mock_session.fetch_token.side_effect = Exception(
            "invalid_token: The token is invalid or has expired"
        )
        oauth.session = mock_session

        with raises(InvalidTokenException) as exc_info:
            oauth.fetch_token("callback_url")
        assert exc_info.value.status_code == 401
        assert exc_info.value.error_type == "invalid_token"
        assert "invalid_token" in str(exc_info.value)

    def test_fetch_token_catches_oauth_errors(self, oauth):
        """Test fetch_token correctly wraps exceptions in OAuthException"""
        # Local imports
        from fitbit_client.exceptions import OAuthException

        # Create an unhandled exception type
        original_error = ValueError("Unhandled OAuth error")
        mock_session = Mock()
        mock_session.fetch_token.side_effect = original_error
        oauth.session = mock_session

        # Setup logger mock to capture log message
        mock_logger = Mock()
        oauth.logger = mock_logger

        # The method should wrap the ValueError in an OAuthException
        with raises(OAuthException) as exc_info:
            oauth.fetch_token("callback_url")

        # Verify the wrapped exception has correct attributes
        assert "Unhandled OAuth error" in str(exc_info.value)
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "oauth"

        # Verify the error was logged correctly
        mock_logger.error.assert_called_once()
        log_message = mock_logger.error.call_args[0][0]
        assert "OAuthException" in log_message
        assert "during token fetch" in log_message

    def test_fetch_token_no_matching_error_type(self, oauth):
        """Test fetch_token when no error type matches in ERROR_TYPE_EXCEPTIONS"""
        # Local imports
        from fitbit_client.exceptions import OAuthException

        # Create a mock response with an error message that doesn't match any error types
        original_error = Exception("Some completely unknown error type")
        mock_session = Mock()
        mock_session.fetch_token.side_effect = original_error
        oauth.session = mock_session

        # Setup logger mock to capture log message
        mock_logger = Mock()
        oauth.logger = mock_logger

        # The method should fall through to the default OAuthException
        with raises(OAuthException) as exc_info:
            oauth.fetch_token("callback_url")

        # Verify the wrapped exception has correct attributes
        assert str(original_error) in str(exc_info.value)
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "oauth"

        # Verify the error was logged correctly with the specific message format
        mock_logger.error.assert_called_once()
        log_message = mock_logger.error.call_args[0][0]
        assert "OAuthException during token fetch" in log_message
        assert original_error.__class__.__name__ in log_message
        assert str(original_error) in log_message

    # Token Refresh Tests
    def test_refresh_token_returns_typed_dict(self, oauth):
        """Test that refresh_token correctly returns a properly typed TokenDict"""
        mock_token_data = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "expires_at": time() + 3600,
            "scope": ["activity", "heartrate"],
        }

        # Mock the session's refresh_token method to return our test data
        mock_session = Mock()
        mock_session.refresh_token.return_value = mock_token_data
        oauth.session = mock_session

        # Also mock _save_token to avoid side effects
        mock_save_token = Mock()
        oauth._save_token = mock_save_token

        # Call the method we're testing
        result = oauth.refresh_token("old_refresh_token")

        # Verify the result is correctly typed and matches our test data
        assert result == mock_token_data
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["access_token"] == "new_access_token"
        assert result["refresh_token"] == "new_refresh_token"

        # Verify the session's refresh_token was called with correct parameters
        mock_session.refresh_token.assert_called_once()
        mock_save_token.assert_called_once_with(mock_token_data)

    def test_refresh_token_expired(self, oauth):
        """Test handling of expired refresh token"""
        mock_session = Mock()
        mock_session.refresh_token.side_effect = Exception(
            "expired_token: The access token expired"
        )
        oauth.session = mock_session

        with raises(ExpiredTokenException) as exc_info:
            oauth.refresh_token("old_token")
        assert exc_info.value.status_code == 401
        assert exc_info.value.error_type == "expired_token"
        assert "expired_token" in str(exc_info.value)

    def test_refresh_token_invalid(self, oauth):
        """Test handling of invalid refresh token"""
        mock_session = Mock()
        mock_session.refresh_token.side_effect = Exception(
            "invalid_grant: The refresh token is invalid"
        )
        oauth.session = mock_session

        with raises(InvalidGrantException) as exc_info:
            oauth.refresh_token("bad_token")
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "invalid_grant"
        assert "invalid_grant" in str(exc_info.value)

    def test_refresh_token_wraps_unexpected_errors(self, oauth):
        """Test that refresh_token wraps unexpected errors in OAuthException"""
        # Local imports
        from fitbit_client.exceptions import OAuthException

        mock_session = Mock()
        unexpected_error = ValueError("unexpected error")
        mock_session.refresh_token.side_effect = unexpected_error
        oauth.session = mock_session

        # Setup logger mock to capture log message
        mock_logger = Mock()
        oauth.logger = mock_logger

        # The method should wrap the ValueError in an OAuthException
        with raises(OAuthException) as exc_info:
            oauth.refresh_token("test_token")

        # Verify the wrapped exception has correct attributes
        assert "unexpected error" in str(exc_info.value)
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "oauth"

        # Verify the error was logged correctly
        mock_logger.error.assert_called_once()
        log_message = mock_logger.error.call_args[0][0]
        assert "OAuthException during token refresh" in log_message

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

    def test_load_token_oserror_exception(self, oauth):
        """Test handling of OSError exception during token loading"""
        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", side_effect=OSError("permission denied")),
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
            "expires_at": time() - 3600,
        }  # 1 hour in the past

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
            "expires_at": time() - 3600,
        }  # 1 hour in the past

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
