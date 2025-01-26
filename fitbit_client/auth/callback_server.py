# fitbit_client/auth/callback_server.py

# Standard library imports
from datetime import datetime
from datetime import timedelta
from http.server import HTTPServer
from logging import getLogger
from os import unlink
from ssl import PROTOCOL_TLS_SERVER
from ssl import SSLContext
from tempfile import NamedTemporaryFile
from threading import Thread
from time import sleep
from time import time
from typing import IO
from typing import Optional
from urllib.parse import urlparse

# Third party imports
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from cryptography.x509.oid import NameOID

# Local imports
from fitbit_client.auth.callback_handler import CallbackHandler


class CallbackServer:
    """Local HTTPS server to handle OAuth2 callbacks"""

    def __init__(self, redirect_uri: str) -> None:
        """Initialize callback server

        Args:
            redirect_uri: Complete OAuth redirect URI
        """
        self.logger = getLogger("fitbit_client.callback_server")
        self.logger.debug(f"Initializing callback server for {redirect_uri}")

        parsed = urlparse(redirect_uri)

        if parsed.scheme != "https":
            error_msg = f"Redirect URI must use HTTPS, got {parsed.scheme}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        self.host: str = parsed.hostname or "localhost"
        self.port: int = parsed.port or 8080
        self.server: Optional[HTTPServer] = None
        self.oauth_response: Optional[str] = None
        self.cert_file: Optional[IO[bytes]] = None
        self.key_file: Optional[IO[bytes]] = None

    def start(self) -> None:
        """Start callback server in background thread"""
        self.logger.debug(f"Starting HTTPS server on {self.host}:{self.port}")
        self.server = HTTPServer((self.host, self.port), CallbackHandler)

        # Create SSL context and certificate
        self.logger.debug("Creating SSL context and certificate")
        context = SSLContext(PROTOCOL_TLS_SERVER)

        # Generate key
        private_key = generate_private_key(public_exponent=65537, key_size=2048)
        self.logger.debug("Generated private key")

        # Generate certificate
        subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, self.host)])
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=10))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName(self.host)]), critical=False)
            .sign(private_key, hashes.SHA256())
        )
        self.logger.debug("Generated self-signed certificate")

        # Create temporary files for cert and key
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

        # Load the cert and key into SSL context
        context.load_cert_chain(certfile=self.cert_file.name, keyfile=self.key_file.name)

        # Wrap the socket
        self.server.socket = context.wrap_socket(self.server.socket, server_side=True)

        setattr(self.server, "last_callback", None)
        self.logger.info(f"HTTPS server started on {self.host}:{self.port}")

        # Start server in background thread
        thread = Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.logger.debug("Server thread started")

    def wait_for_callback(self, timeout: int = 300) -> Optional[str]:
        """Wait for OAuth callback

        Args:
            timeout: How long to wait for callback in seconds

        Returns:
            Optional[str]: Full callback URL with auth parameters or None if timeout
        """
        if not self.server:
            error_msg = "Server not started"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

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
        return None

    def stop(self) -> None:
        """Stop callback server and clean up resources"""
        self.logger.debug("Stopping callback server")
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.logger.debug("Server stopped")

        # Clean up temp files
        if self.cert_file:
            self.logger.debug(f"Removing temporary certificate file: {self.cert_file.name}")
            unlink(self.cert_file.name)
            self.cert_file = None

        if self.key_file:
            self.logger.debug(f"Removing temporary key file: {self.key_file.name}")
            unlink(self.key_file.name)
            self.key_file = None

        self.logger.info("Callback server stopped and resources cleaned up")
