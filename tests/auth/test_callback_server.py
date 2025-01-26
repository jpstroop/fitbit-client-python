# tests/auth/test_callback_server.py

# Standard library imports
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.auth.callback_server import CallbackServer


class TestCallbackServer:
    @fixture
    def server(self):
        """Create a CallbackServer instance with standard test configuration"""
        with (
            patch("fitbit_client.auth.callback_server.HTTPServer"),
            patch("fitbit_client.auth.callback_server.Thread"),
        ):
            server = CallbackServer("https://localhost:8080")
            return server

    def test_initialization(self):
        """Test server initialization with various URI formats"""
        server = CallbackServer("https://localhost")
        assert server.host == "localhost"
        assert server.port == 8080

        server = CallbackServer("https://localhost:9090")
        assert server.host == "localhost"
        assert server.port == 9090

        with raises(ValueError) as exc_info:
            CallbackServer("http://localhost:8080")
        assert "HTTPS" in str(exc_info.value)

    @patch("fitbit_client.auth.callback_server.HTTPServer")
    @patch("fitbit_client.auth.callback_server.Thread")
    @patch("fitbit_client.auth.callback_server.SSLContext")
    def test_server_start(self, mock_ssl_context, mock_thread, mock_http_server):
        """Test server startup process"""
        server = CallbackServer("https://localhost:8080")

        with patch("fitbit_client.auth.callback_server.NamedTemporaryFile"):
            server.start()

            assert mock_ssl_context.called
            assert mock_thread.called
            mock_thread.return_value.start.assert_called_once()

    def test_wait_for_callback(self, server):
        """Test callback waiting functionality"""
        server.server = Mock()

        setattr(server.server, "last_callback", "/callback?code=test")
        response = server.wait_for_callback(timeout=1)
        assert response == "/callback?code=test"

        setattr(server.server, "last_callback", None)
        response = server.wait_for_callback(timeout=1)
        assert response is None

    def test_server_cleanup(self, server):
        """Test server cleanup and resource management"""
        server.server = Mock()
        server.cert_file = Mock()
        server.cert_file.name = "test_cert.pem"
        server.key_file = Mock()
        server.key_file.name = "test_key.pem"

        with patch("fitbit_client.auth.callback_server.unlink") as mock_unlink:
            server.stop()

            assert server.server.shutdown.called
            assert server.server.server_close.called
            assert mock_unlink.call_count == 2
