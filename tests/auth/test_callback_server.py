# tests/auth/test_callback_server.py

# Standard library imports
from ssl import SSLError
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from cryptography.hazmat.primitives.asymmetric import rsa
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.auth.callback_server import CallbackServer
from fitbit_client.exceptions import InvalidRequestException
from fitbit_client.exceptions import SystemException


class TestCallbackServer:
    @fixture
    def mock_private_key(self):
        """Create a properly mocked RSA private key"""
        mock_key = MagicMock(spec=rsa.RSAPrivateKey)
        mock_public_key = MagicMock(spec=rsa.RSAPublicKey)
        mock_key.public_key.return_value = mock_public_key
        mock_key.private_bytes.return_value = b"mock private key"
        return mock_key

    @fixture
    def mock_certificate(self):
        """Create a mock certificate"""
        mock_cert = MagicMock()
        mock_cert.public_bytes.return_value = b"mock certificate"
        return mock_cert

    @fixture
    def mock_ssl_context(self):
        """Create a mock SSL context"""
        with patch("fitbit_client.auth.callback_server.SSLContext") as mock_context_class:
            mock_context = MagicMock()
            mock_context_class.return_value = mock_context
            mock_context.wrap_socket.return_value = MagicMock()
            yield mock_context

    @fixture
    def server(self):
        """Create a CallbackServer instance with network operations disabled"""
        with patch("fitbit_client.auth.callback_server.getLogger"):
            return CallbackServer("https://localhost:8080")

    # Initialization Tests
    def test_initialization_requires_https(self):
        """Test that non-HTTPS URIs are rejected"""
        with raises(InvalidRequestException) as exc_info:
            CallbackServer("http://localhost:8080")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "invalid_request"
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

    def test_create_handler(self, server):
        """Test the factory function for creating CallbackHandler instances"""
        mock_request = MagicMock()
        mock_client_address = ("127.0.0.1", 1234)
        mock_server = MagicMock()

        # Patch the CallbackHandler to verify it gets instantiated correctly
        with patch("fitbit_client.auth.callback_server.CallbackHandler") as mock_handler_class:
            mock_handler = MagicMock()
            mock_handler_class.return_value = mock_handler

            # Call the method under test
            handler = server.create_handler(mock_request, mock_client_address, mock_server)

            # Verify the CallbackHandler was instantiated with the correct arguments
            mock_handler_class.assert_called_once_with(
                mock_request, mock_client_address, mock_server
            )

            # Verify the return value
            assert handler is mock_handler

    # Server Start Tests
    def test_start_server_sets_callback_attribute(
        self, server, mock_private_key, mock_certificate, mock_ssl_context
    ):
        """Test that server initialization sets last_callback attribute"""
        mock_server = MagicMock()
        mock_server.socket = MagicMock()

        cert_file = MagicMock()
        cert_file.name = "cert.pem"
        cert_file.closed = False

        key_file = MagicMock()
        key_file.name = "key.pem"
        key_file.closed = False

        temp_files = [cert_file, key_file]
        mock_temp_file_constructor = MagicMock(side_effect=temp_files)

        with (
            patch("fitbit_client.auth.callback_server.HTTPServer", return_value=mock_server),
            patch(
                "fitbit_client.auth.callback_server.generate_private_key",
                return_value=mock_private_key,
            ),
            patch("cryptography.x509.CertificateBuilder.sign", return_value=mock_certificate),
            patch("tempfile.NamedTemporaryFile", mock_temp_file_constructor),
            patch("threading.Thread"),
        ):
            server.start()

            assert hasattr(mock_server, "last_callback")
            assert mock_server.last_callback is None

    def test_generic_startup_error(self, server):
        """Test handling of generic startup errors"""
        with patch(
            "fitbit_client.auth.callback_server.HTTPServer",
            side_effect=Exception("Generic server error"),
        ):
            with raises(SystemException) as exc_info:
                server.start()

            assert exc_info.value.status_code == 500
            assert exc_info.value.error_type == "system"
            assert "Failed to start callback server" in str(exc_info.value)

    def test_key_generation_error(self, server):
        """Test handling of SSL key generation failure"""
        mock_server = MagicMock()

        with (
            patch("fitbit_client.auth.callback_server.HTTPServer", return_value=mock_server),
            patch(
                "fitbit_client.auth.callback_server.generate_private_key",
                side_effect=Exception("Key generation failed"),
            ),
        ):
            with raises(SystemException) as exc_info:
                server.start()

            assert exc_info.value.status_code == 500
            assert exc_info.value.error_type == "system"
            assert "Failed to generate SSL key" in str(exc_info.value)

    def test_certificate_generation_error(self, server, mock_private_key):
        """Test handling of certificate generation failure"""
        mock_server = MagicMock()

        with (
            patch("fitbit_client.auth.callback_server.HTTPServer", return_value=mock_server),
            patch(
                "fitbit_client.auth.callback_server.generate_private_key",
                return_value=mock_private_key,
            ),
            patch(
                "cryptography.x509.CertificateBuilder.sign",
                side_effect=Exception("Certificate generation failed"),
            ),
        ):
            with raises(SystemException) as exc_info:
                server.start()

            assert exc_info.value.status_code == 500
            assert exc_info.value.error_type == "system"
            assert "Failed to generate SSL certificate" in str(exc_info.value)

    def test_start_server_file_write_error(
        self, server, mock_private_key, mock_certificate, mock_ssl_context
    ):
        """Test handling of SSL file write errors"""
        mock_server = MagicMock()
        mock_server.socket = MagicMock()

        cert_file = MagicMock()
        cert_file.name = "cert.pem"
        cert_file.closed = False
        cert_file.write = MagicMock(side_effect=Exception("File write failed"))

        key_file = MagicMock()
        key_file.name = "key.pem"
        key_file.closed = False

        with (
            patch("fitbit_client.auth.callback_server.HTTPServer", return_value=mock_server),
            patch(
                "fitbit_client.auth.callback_server.generate_private_key",
                return_value=mock_private_key,
            ),
            patch("cryptography.x509.CertificateBuilder.sign", return_value=mock_certificate),
            patch(
                "fitbit_client.auth.callback_server.NamedTemporaryFile",
                side_effect=[cert_file, key_file],
            ),
        ):
            with raises(SystemException) as exc_info:
                server.start()

            assert exc_info.value.status_code == 500
            assert exc_info.value.error_type == "system"
            assert "Failed to write SSL files" in str(exc_info.value)

    def test_start_server_ssl_error(
        self, server, mock_private_key, mock_certificate, mock_ssl_context
    ):
        """Test handling of SSL configuration errors"""
        mock_server = MagicMock()
        mock_server.socket = MagicMock()

        cert_file = MagicMock()
        cert_file.name = "cert.pem"
        cert_file.closed = False

        key_file = MagicMock()
        key_file.name = "key.pem"
        key_file.closed = False

        mock_ssl_context.load_cert_chain.side_effect = SSLError("SSL Error")

        with (
            patch("fitbit_client.auth.callback_server.HTTPServer", return_value=mock_server),
            patch(
                "fitbit_client.auth.callback_server.generate_private_key",
                return_value=mock_private_key,
            ),
            patch("cryptography.x509.CertificateBuilder.sign", return_value=mock_certificate),
            patch("tempfile.NamedTemporaryFile", side_effect=[cert_file, key_file]),
        ):
            with raises(SystemException) as exc_info:
                server.start()

            assert exc_info.value.status_code == 500
            assert exc_info.value.error_type == "system"
            assert "Failed to load SSL certificate" in str(exc_info.value)

    def test_socket_wrap_error(self, server, mock_private_key, mock_certificate):
        """Test handling of socket wrapping failure"""
        mock_server = MagicMock()
        mock_context = MagicMock()
        mock_context.wrap_socket.side_effect = Exception("Socket wrap failed")

        with (
            patch("fitbit_client.auth.callback_server.HTTPServer", return_value=mock_server),
            patch(
                "fitbit_client.auth.callback_server.generate_private_key",
                return_value=mock_private_key,
            ),
            patch("cryptography.x509.CertificateBuilder.sign", return_value=mock_certificate),
            patch("fitbit_client.auth.callback_server.SSLContext", return_value=mock_context),
            patch("tempfile.NamedTemporaryFile", side_effect=[MagicMock(), MagicMock()]),
        ):
            with raises(SystemException) as exc_info:
                server.start()

            assert exc_info.value.status_code == 500
            assert exc_info.value.error_type == "system"
            assert "Failed to configure SSL socket" in str(exc_info.value)

    def test_start_server_thread_error(self, server, mock_private_key, mock_certificate):
        """Test handling of server thread start errors"""
        mock_server = MagicMock()
        mock_server.socket = MagicMock()

        cert_file = MagicMock()
        cert_file.name = "cert.pem"
        cert_file.write = MagicMock()
        cert_file.close = MagicMock()

        key_file = MagicMock()
        key_file.name = "key.pem"
        key_file.write = MagicMock()
        key_file.close = MagicMock()

        mock_context = MagicMock()
        mock_context.wrap_socket.return_value = MagicMock()

        def thread_that_fails(*args, **kwargs):
            print("Thread being constructed with:", args, kwargs)
            raise Exception("Thread start failed")

        mock_thread = MagicMock(side_effect=thread_that_fails)

        with (
            patch("fitbit_client.auth.callback_server.HTTPServer", return_value=mock_server),
            patch(
                "fitbit_client.auth.callback_server.generate_private_key",
                return_value=mock_private_key,
            ),
            patch("cryptography.x509.CertificateBuilder.sign", return_value=mock_certificate),
            patch(
                "fitbit_client.auth.callback_server.NamedTemporaryFile",
                side_effect=[cert_file, key_file],
            ),
            patch("fitbit_client.auth.callback_server.SSLContext", return_value=mock_context),
            patch("fitbit_client.auth.callback_server.Thread", mock_thread),
        ):
            with raises(SystemException) as exc_info:
                server.start()

            assert exc_info.value.status_code == 500
            assert exc_info.value.error_type == "system"
            assert "Failed to start server thread" in str(exc_info.value)

    # Callback Handling Tests
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
        assert exc_info.value.field_name == "oauth_callback"
        assert "1 seconds" in str(exc_info.value)

    def test_wait_for_callback_success(self, server):
        """Test successful callback handling"""
        server.server = Mock()
        callback_data = "/callback?code=test_code"
        setattr(server.server, "last_callback", callback_data)

        result = server.wait_for_callback()
        assert result == callback_data

    # Server Stop/Cleanup Tests
    def test_stop_server_removes_temp_files(self, server):
        """Test that temporary files are cleaned up"""
        with patch("fitbit_client.auth.callback_server.unlink") as mock_unlink:
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

    def test_stop_server_handles_shutdown_error(self, server):
        """Test handling of server shutdown errors"""
        mock_server = Mock()
        mock_server.shutdown.side_effect = Exception("Shutdown failed")
        server.server = mock_server
        mock_logger = Mock()
        server.logger = mock_logger

        server.stop()

        # Verify error was logged
        mock_logger.error.assert_called_once()
        assert "Error stopping server" in mock_logger.error.call_args[0][0]

    def test_server_cleanup_on_stop(self, server):
        """Test server cleanup and file removal during stop"""
        # Set up mocked server and files
        server.server = MagicMock()
        server.cert_file = MagicMock()
        server.cert_file.name = "cert.pem"
        server.key_file = MagicMock()
        server.key_file.name = "key.pem"

        with patch("fitbit_client.auth.callback_server.unlink") as mock_unlink:
            server.stop()

            # Verify server shutdown was called
            assert server.server.shutdown.called
            assert server.server.server_close.called

            # Verify file cleanup
            mock_unlink.assert_any_call("cert.pem")
            mock_unlink.assert_any_call("key.pem")

            # Verify files were nulled
            assert server.cert_file is None
            assert server.key_file is None

    def test_server_cleanup(self, server):
        """Test server shutdown and start of file cleanup process"""
        # Initialize mocks
        server.server = MagicMock()
        server.logger = MagicMock()
        server.cert_file = MagicMock()

        # Simulate both paths - success and failure
        server.stop()  # First call with normal shutdown

        # Reset mocks
        server.server.reset_mock()
        server.logger.reset_mock()

        # Make shutdown fail on second try
        server.server.shutdown.side_effect = Exception("Failed")
        server.stop()  # Second call with failed shutdown

        # Reset and remove server to test that path
        server.server = None
        server.stop()  # Third call with no server
