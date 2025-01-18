# auth/callback_handler.py
# Standard library imports
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from urllib.parse import urlparse


class CallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth2 callback requests"""

    def do_GET(self):
        """Process GET request and extract OAuth parameters"""
        # Parse query parameters
        query_components = parse_qs(urlparse(self.path).query)

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
                <script>window.close();</script>
            </body>
        </html>
        """

        self.wfile.write(response.encode("utf-8"))

        # Store query parameters in server instance
        if hasattr(self.server, "oauth_response"):
            self.server.oauth_response = self.path

    def log_message(self, format, *args):
        """Suppress logging output"""
        pass
