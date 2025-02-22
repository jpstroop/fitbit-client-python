# fitbit_client/auth/callback_handler.py

# Standard library imports
from http.server import BaseHTTPRequestHandler
from logging import getLogger
from typing import Dict
from urllib.parse import parse_qs
from urllib.parse import urlparse

# Local imports
from fitbit_client.exceptions import InvalidGrantException
from fitbit_client.exceptions import InvalidRequestException


class CallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth2 callback requests"""

    def __init__(self, *args, **kwargs) -> None:
        self.logger = getLogger("fitbit_client.callback_handler")
        super().__init__(*args, **kwargs)

    def parse_query_parameters(self) -> Dict[str, str]:
        """Parse and validate query parameters from callback URL

        Returns:
            Dictionary of parsed parameters

        Raises:
            InvalidRequestException: If required parameters are missing
            InvalidGrantException: If authorization code is invalid/expired
        """
        query_components = parse_qs(urlparse(self.path).query)
        self.logger.debug(f"Query parameters: {query_components}")

        # Check for error response
        if "error" in query_components:
            error_type = query_components["error"][0]
            error_desc = query_components.get("error_description", ["Unknown error"])[0]

            if error_type == "invalid_grant":
                raise InvalidGrantException(
                    message=error_desc, status_code=400, error_type="invalid_grant"
                )
            else:
                raise InvalidRequestException(
                    message=error_desc, status_code=400, error_type=error_type
                )

        # Check for required parameters
        required_params = ["code", "state"]
        missing_params = [param for param in required_params if param not in query_components]
        if missing_params:
            raise InvalidRequestException(
                message=f"Missing required parameters: {', '.join(missing_params)}",
                status_code=400,
                error_type="invalid_request",
                field_name="callback_params",
            )

        return {k: v[0] for k, v in query_components.items()}

    def send_success_response(self) -> None:
        """Send successful authentication response to browser"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

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

    def send_error_response(self, error_message: str) -> None:
        """Send error response to browser"""
        self.send_response(400)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        response = f"""
        <html>
            <body>
                <h1>Authentication Error</h1>
                <p>{error_message}</p>
                <p>You can close this window and try again.</p>
                <script>setTimeout(() => window.close(), 10000);</script>
            </body>
        </html>
        """

        self.wfile.write(response.encode("utf-8"))
        self.logger.debug("Sent error response to browser")

    def do_GET(self) -> None:
        """Process GET request and extract OAuth parameters

        This handles the OAuth2 callback, including:
        - Parameter validation
        - Error handling
        - Success/error responses
        - Storing callback data for the server
        """
        self.logger.debug(f"Received callback request: {self.path}")

        try:
            # Parse and validate query parameters
            self.parse_query_parameters()

            # Send success response
            self.send_success_response()

            # Store validated callback in server instance
            setattr(self.server, "last_callback", self.path)
            self.logger.debug("OAuth callback received and validated successfully")

        except (InvalidRequestException, InvalidGrantException) as e:
            # Send error response to browser
            self.send_error_response(str(e))
            # Re-raise for server to handle
            raise

    def log_message(self, format: str, *args: str) -> None:
        """Override default logging to use our logger instead"""
        self.logger.debug(f"Server log: {format%args}")
