# fitbit_client/auth/callback_server.py

# Standard library imports
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from http.server import HTTPServer
from logging import getLogger
from os import unlink
from ssl import PROTOCOL_TLS_SERVER
from ssl import SSLContext
from ssl import SSLError
from tempfile import NamedTemporaryFile
from threading import Thread
from time import sleep
from time import time
from typing import Any
from typing import IO
from typing import Optional
from typing import Tuple
from urllib.parse import urlparse

# Third party imports
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from cryptography.x509.oid import NameOID

# Local imports
from fitbit_client.auth.callback_handler import CallbackHandler
from fitbit_client.exceptions import InvalidRequestException
from fitbit_client.exceptions import SystemException


class CallbackServer:
    """Local HTTPS server to handle OAuth2 callbacks"""

    def __init__(self, redirect_uri: str) -> None:
        """Initialize callback server

        Args:
            redirect_uri: Complete OAuth redirect URI (must be HTTPS)

        Raises:
            InvalidRequestException: If redirect_uri doesn't use HTTPS or is invalid
        """
        self.logger = getLogger("fitbit_client.callback_server")
        self.logger.debug(f"Initializing callback server for {redirect_uri}")

        parsed = urlparse(redirect_uri)

        if parsed.scheme != "https":
            raise InvalidRequestException(
                message="Request to invalid domain: redirect_uri must use HTTPS protocol.",
                status_code=400,
                error_type="invalid_request",
                field_name="redirect_uri",
            )

        if not parsed.hostname:
            raise InvalidRequestException(
                message="Invalid redirect_uri parameter value",
                status_code=400,
                error_type="invalid_request",
                field_name="redirect_uri",
            )

        self.host: str = parsed.hostname
        self.port: int = parsed.port or 8080
        self.server: Optional[HTTPServer] = None
        self.oauth_response: Optional[str] = None
        self.cert_file: Optional[IO[bytes]] = None
        self.key_file: Optional[IO[bytes]] = None

    def create_handler(
        self, request: Any, client_address: Tuple[str, int], server: HTTPServer
    ) -> CallbackHandler:
        """Factory function to create CallbackHandler instances.

        Args:
            request: The request from the client
            client_address: The client's address
            server: The HTTPServer instance

        Returns:
            A new CallbackHandler instance
        """
        return CallbackHandler(request, client_address, server)

    def start(self) -> None:
        """
        Start callback server in background thread

        Raises:
            SystemException: If there's an error starting the server or configuring SSL
        """
        self.logger.debug(f"Starting HTTPS server on {self.host}:{self.port}")

        try:
            # Use the factory function instead of directly passing CallbackHandler class
            self.server = HTTPServer((self.host, self.port), self.create_handler)

            # Create SSL context and certificate
            self.logger.debug("Creating SSL context and certificate")
            context = SSLContext(PROTOCOL_TLS_SERVER)

            # Generate key
            try:
                private_key = generate_private_key(public_exponent=65537, key_size=2048)
                self.logger.debug("Generated private key")
            except Exception as e:
                raise SystemException(
                    message=f"Failed to generate SSL key: {str(e)}",
                    status_code=500,
                    error_type="system",
                )

            # Generate certificate
            try:
                subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, self.host)])
                cert = (
                    x509.CertificateBuilder()
                    .subject_name(subject)
                    .issuer_name(issuer)
                    .public_key(private_key.public_key())
                    .serial_number(x509.random_serial_number())
                    .not_valid_before(datetime.now(UTC))
                    .not_valid_after(datetime.now(UTC) + timedelta(days=10))
                    .add_extension(
                        x509.SubjectAlternativeName([x509.DNSName(self.host)]), critical=False
                    )
                    .sign(private_key, hashes.SHA256())
                )
                self.logger.debug("Generated self-signed certificate")
            except Exception as e:
                raise SystemException(
                    message=f"Failed to generate SSL certificate: {str(e)}",
                    status_code=500,
                    error_type="system",
                )

            # Create temporary files for cert and key
            try:
                self.cert_file = NamedTemporaryFile(mode="wb", delete=False)
                self.key_file = NamedTemporaryFile(mode="wb", delete=False)

                # Write cert and key to temp files
                self.cert_file.write(cert.public_bytes(serialization.Encoding.PEM))
                self.key_file.write(
                    private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption(),
                    )
                )
                self.cert_file.close()
                self.key_file.close()
                self.logger.debug("Wrote certificate and key to temporary files")
            except Exception as e:
                raise SystemException(
                    message=f"Failed to write SSL files: {str(e)}",
                    status_code=500,
                    error_type="system",
                )

            # Load the cert and key into SSL context
            try:
                context.load_cert_chain(certfile=self.cert_file.name, keyfile=self.key_file.name)
            except SSLError as e:
                raise SystemException(
                    message=f"Failed to load SSL certificate: {str(e)}",
                    status_code=500,
                    error_type="system",
                )

            # Wrap the socket
            try:
                self.server.socket = context.wrap_socket(self.server.socket, server_side=True)
            except Exception as e:
                raise SystemException(
                    message=f"Failed to configure SSL socket: {str(e)}",
                    status_code=500,
                    error_type="system",
                )

            setattr(self.server, "last_callback", None)
            self.logger.debug(f"HTTPS server started on {self.host}:{self.port}")

            # Start server in background thread
            try:
                thread = Thread(target=self.server.serve_forever, daemon=True)
                thread.start()
                self.logger.debug("Server thread started")
            except Exception as e:
                raise SystemException(
                    message=f"Failed to start server thread: {str(e)}",
                    status_code=500,
                    error_type="system",
                )

        except Exception as e:
            # Only catch non-SystemException exceptions here
            if not isinstance(e, SystemException):
                error_msg = f"Failed to start callback server: {str(e)}"
                self.logger.error(error_msg)
                raise SystemException(message=error_msg, status_code=500, error_type="system")
            raise

    def wait_for_callback(self, timeout: int = 300) -> Optional[str]:
        """Wait for OAuth callback

        Args:
            timeout: How long to wait for callback in seconds

        Returns:
            Optional[str]: Full callback URL with auth parameters or None if timeout

        Raises:
            SystemException: If server was not started
            InvalidRequestException: If callback times out
        """
        if not self.server:
            raise SystemException(
                message="Server not started", status_code=500, error_type="system"
            )

        self.logger.debug(f"Waiting for callback (timeout: {timeout}s)")
        # Wait for response with timeout
        start_time = time()
        while time() - start_time < timeout:
            if hasattr(self.server, "last_callback") and getattr(self.server, "last_callback"):
                self.oauth_response = getattr(self.server, "last_callback")
                self.logger.debug("Received callback")
                return self.oauth_response
            sleep(0.1)

        self.logger.error("Callback wait timed out")
        raise InvalidRequestException(
            message=f"OAuth callback timed out after {timeout} seconds",
            status_code=400,
            error_type="invalid_request",
            field_name="oauth_callback",
        )

    def stop(self) -> None:
        """Stop callback server and clean up resources"""
        self.logger.debug("Stopping callback server")
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
                self.logger.debug("Server stopped")
            except Exception as e:
                self.logger.error(f"Error stopping server: {str(e)}")

        # Clean up temp files
        if self.cert_file:
            try:
                self.logger.debug(f"Removing temporary certificate file: {self.cert_file.name}")
                unlink(self.cert_file.name)
            except Exception as e:
                self.logger.warning(f"Failed to remove certificate file: {str(e)}")
            self.cert_file = None

        if self.key_file:
            try:
                self.logger.debug(f"Removing temporary key file: {self.key_file.name}")
                unlink(self.key_file.name)
            except Exception as e:
                self.logger.warning(f"Failed to remove key file: {str(e)}")
            self.key_file = None

        self.logger.debug("Temporary resources cleaned up")
