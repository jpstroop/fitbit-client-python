# tests/auth/test_callback_handler.py

# Standard library imports
from http.server import BaseHTTPRequestHandler
from io import BytesIO
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.auth.callback_handler import CallbackHandler
from fitbit_client.exceptions import InvalidGrantException
from fitbit_client.exceptions import InvalidRequestException


class TestCallbackHandler:
    @fixture
    def handler(self):
        """Create a CallbackHandler instance with network operations disabled"""
        with patch.object(BaseHTTPRequestHandler, "__init__", return_value=None):
            handler = CallbackHandler(Mock(), ("127.0.0.1", 8080), Mock())
            handler.wfile = BytesIO()  # Mock response output
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            return handler

    def test_successful_callback(self, handler):
        """Test processing of successful callback"""
        handler.path = "/callback?code=test_auth_code&state=test_state"
        handler.server = Mock()

        handler.do_GET()

        # Verify success response
        handler.send_response.assert_called_once_with(200)
        handler.send_header.assert_called_once_with("Content-Type", "text/html")
        handler.end_headers.assert_called_once()

        # Verify response content
        handler.wfile.seek(0)
        response = handler.wfile.getvalue().decode("utf-8")
        assert "Authentication Successful" in response
        assert "setTimeout" in response

        # Verify callback storage
        assert handler.server.last_callback == handler.path

    def test_missing_parameters(self, handler):
        """Test handling of missing required parameters"""
        handler.path = "/callback?code=test_auth_code"  # Missing state

        with raises(InvalidRequestException) as exc_info:
            handler.do_GET()

        assert "Missing required parameters: state" in str(exc_info.value)
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "invalid_request"
        assert exc_info.value.field_name == "callback_params"

        # Verify error response
        handler.wfile.seek(0)
        response = handler.wfile.getvalue().decode("utf-8")
        assert "Authentication Error" in response
        assert "Missing required parameters" in response

    def test_invalid_grant_error(self, handler):
        """Test handling of invalid grant error"""
        handler.path = "/callback?error=invalid_grant&error_description=Authorization+code+expired"

        with raises(InvalidGrantException) as exc_info:
            handler.do_GET()

        assert "Authorization code expired" in str(exc_info.value)
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "invalid_grant"

        # Verify error response
        handler.wfile.seek(0)
        response = handler.wfile.getvalue().decode("utf-8")
        assert "Authentication Error" in response
        assert "Authorization code expired" in response

    def test_other_oauth_errors(self, handler):
        """Test handling of other OAuth errors"""
        handler.path = "/callback?error=invalid_request&error_description=Invalid+request"

        with raises(InvalidRequestException) as exc_info:
            handler.do_GET()

        assert "Invalid request" in str(exc_info.value)
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "invalid_request"

        # Verify error response
        handler.wfile.seek(0)
        response = handler.wfile.getvalue().decode("utf-8")
        assert "Authentication Error" in response
        assert "Invalid request" in response

    def test_parse_query_parameters_success(self, handler):
        """Test successful parsing of query parameters"""
        handler.path = "/callback?code=test_code&state=test_state&other=value"

        params = handler.parse_query_parameters()

        assert params["code"] == "test_code"
        assert params["state"] == "test_state"
        assert params["other"] == "value"

    def test_parse_query_parameters_error(self, handler):
        """Test parsing of error parameters"""
        handler.path = "/callback?error=invalid_scope&error_description=Missing+scope"

        with raises(InvalidRequestException) as exc_info:
            handler.parse_query_parameters()

        assert exc_info.value.error_type == "invalid_scope"
        assert "Missing scope" in str(exc_info.value)

    def test_logging_override(self, handler):
        """Test that logging is properly overridden"""
        test_message = "Test log message"
        handler.logger = Mock()

        handler.log_message("%s", test_message)

        handler.logger.debug.assert_called_once_with(f"Server log: {test_message}")

    def test_send_error_response(self, handler):
        """Test error response formatting"""
        error_message = "Test error message"
        handler.send_error_response(error_message)

        # Verify response headers
        handler.send_response.assert_called_once_with(400)
        handler.send_header.assert_called_once_with("Content-Type", "text/html")
        handler.end_headers.assert_called_once()

        # Verify response content
        handler.wfile.seek(0)
        response = handler.wfile.getvalue().decode("utf-8")
        assert "Authentication Error" in response
        assert error_message in response
        assert "setTimeout" in response
