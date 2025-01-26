# fitbit_client/auth/callback_handler.py

# Standard library imports
from http.server import BaseHTTPRequestHandler
from logging import getLogger
from urllib.parse import parse_qs
from urllib.parse import urlparse


class CallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth2 callback requests"""

    def __init__(self, *args, **kwargs) -> None:
        self.logger = getLogger("fitbit_client.callback_handler")
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        """Process GET request and extract OAuth parameters"""
        self.logger.debug(f"Received callback request: {self.path}")

        # Parse query parameters
        query_components = parse_qs(urlparse(self.path).query)
        self.logger.debug(f"Query parameters: {query_components}")

        # Set response headers
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        # Create simple success page
        response = """
        <html>
            <body>
                <h1>Authentication Successful!</h1>
                <p>You can close this window and return to your application.</p>
                <script>setTimeout(() => window.close(), 5000);</script>
            </body>
        </html>
        """

        self.wfile.write(response.encode("utf-8"))
        self.logger.debug("Sent success response to browser")

        # Store query parameters in server instance
        setattr(self.server, "last_callback", self.path)
        self.logger.info("OAuth callback processed successfully")

    def log_message(self, format: str, *args: str) -> None:
        """Override default logging to use our logger instead"""
        self.logger.debug(f"Server log: {format%args}")
