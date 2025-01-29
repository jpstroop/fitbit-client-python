# tests/auth/test_callback_handler.py

# Standard library imports
from http.server import BaseHTTPRequestHandler
from io import BytesIO
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.auth.callback_handler import CallbackHandler


class TestCallbackHandler:
    @fixture
    def handler(self):
        """Create a CallbackHandler instance with network operations disabled"""
        with patch.object(BaseHTTPRequestHandler, "__init__", return_value=None):
            handler = CallbackHandler(Mock(), ("127.0.0.1", 8080), Mock())
            handler.wfile = BytesIO()
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            return handler

    def test_successful_callback_handling(self, handler):
        """Test handling of a successful OAuth callback"""
        handler.path = "/callback?code=test_auth_code&state=test_state"
        handler.server = Mock()

        handler.do_GET()

        handler.send_response.assert_called_once_with(200)
        handler.send_header.assert_called_once_with("Content-Type", "text/html")
        handler.end_headers.assert_called_once()

        handler.wfile.seek(0)
        response = handler.wfile.getvalue().decode("utf-8")
        assert "Authentication Successful" in response
        assert "setTimeout(() => window.close(), 5000);" in response
        assert handler.server.last_callback == handler.path

    def test_callback_with_error(self, handler):
        """Test handling of an OAuth error callback"""
        handler.path = "/callback?error=access_denied&error_description=User+denied+access"
        handler.server = Mock()

        handler.do_GET()

        handler.send_response.assert_called_once_with(200)
        assert handler.server.last_callback == handler.path

    def test_logging_suppression(self, handler):
        """Test that logging is properly suppressed"""
        handler.log_message("Test message %s", "test")
        # Test passes if no exception is raised
