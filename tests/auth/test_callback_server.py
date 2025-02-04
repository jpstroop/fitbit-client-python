# tests/auth/test_callback_server.py

# Standard library imports
from ssl import SSLError
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.auth.callback_server import CallbackServer
from fitbit_client.exceptions import InvalidRequestException
from fitbit_client.exceptions import SystemException


class TestCallbackServer:
    @fixture
    def server(self):
        """Create a CallbackServer instance with network operations disabled"""
        with (
            patch("fitbit_client.auth.callback_server.HTTPServer"),
            patch("fitbit_client.auth.callback_server.Thread"),
            patch("fitbit_client.auth.callback_server.getLogger"),
        ):
            server = CallbackServer("https://localhost:8080")
            return server

    def test_initialization_requires_https(self):
        """Test that non-HTTPS URIs are rejected"""
        with raises(InvalidRequestException) as exc_info:
            CallbackServer("http://localhost:8080")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "request"
        assert exc_info.value.field_name == "redirect_uri"
        assert "must use HTTPS protocol" in str(exc_info.value)

    def test_initialization_validates_uri(self):
        """Test that invalid URIs are rejected"""
        with raises(InvalidRequestException) as exc_info:
            CallbackServer("https://")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "invalid_request"
        assert exc_info.value.field_name == "redirect_uri"
        assert "Invalid redirect_uri" in str(exc_info.value)

    def test_initialization_with_valid_uri(self):
        """Test initialization with valid URI"""
        with patch("fitbit_client.auth.callback_server.getLogger"):
            server = CallbackServer("https://localhost:8080")
            assert server.host == "localhost"
            assert server.port == 8080

    def test_start_server_ssl_error(self, server):
        """Test handling of SSL configuration errors"""
        with patch("ssl.SSLContext.load_cert_chain", side_effect=SSLError("SSL Error")):
            with raises(SystemException) as exc_info:
                server.start()

            assert exc_info.value.status_code == 500
            assert exc_info.value.error_type == "system"
            assert "Failed to load SSL certificate" in str(exc_info.value)

    def test_start_server_general_error(self, server):
        """Test handling of general server startup errors"""
        with patch(
            "fitbit_client.auth.callback_server.HTTPServer", side_effect=Exception("Server Error")
        ):
            with raises(SystemException) as exc_info:
                server.start()

    def test_wait_for_callback_server_not_started(self, server):
        """Test that waiting without starting server raises error"""
        with raises(SystemException) as exc_info:
            server.wait_for_callback()

        assert exc_info.value.status_code == 500
        assert exc_info.value.error_type == "system"
        assert "Server not started" in str(exc_info.value)

    def test_wait_for_callback_timeout(self, server):
        """Test callback timeout handling"""
        server.server = Mock()
        setattr(server.server, "last_callback", None)

        with raises(InvalidRequestException) as exc_info:
            server.wait_for_callback(timeout=1)

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "invalid_request"
        assert "timed out" in str(exc_info.value)

    def test_wait_for_callback_success(self, server):
        """Test successful callback handling"""
        server.server = Mock()
        callback_data = "/callback?code=test_code"
        setattr(server.server, "last_callback", callback_data)

        result = server.wait_for_callback()
        assert result == callback_data

    def test_stop_server_removes_temp_files(self, server):
        """Test that temporary files are cleaned up"""
        with patch("fitbit_client.auth.callback_server.unlink") as mock_unlink:
            # Setup mock temp files
            server.cert_file = Mock()
            server.cert_file.name = "test_cert.pem"
            server.key_file = Mock()
            server.key_file.name = "test_key.pem"
            server.server = Mock()

            server.stop()

            # Verify server shutdown
            assert server.server.shutdown.called
            assert server.server.server_close.called

            # Verify file cleanup
            mock_unlink.assert_any_call("test_cert.pem")
            mock_unlink.assert_any_call("test_key.pem")

    def test_stop_server_handles_cleanup_errors(self, server):
        """Test handling of file cleanup errors"""
        with patch(
            "fitbit_client.auth.callback_server.unlink", side_effect=Exception("Cleanup Error")
        ):
            # Setup mock temp files
            server.cert_file = Mock()
            server.cert_file.name = "test_cert.pem"
            server.key_file = Mock()
            server.key_file.name = "test_key.pem"
            server.server = Mock()

            # Should not raise exception
            server.stop()

            # Verify server was still shut down
            assert server.server.shutdown.called
            assert server.server.server_close.called
