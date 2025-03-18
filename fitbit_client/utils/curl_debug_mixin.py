# fitbit_client/utils/curl_debug_mixin.py

"""
Mixin for generating curl commands for API debugging.
"""

# Standard library imports
from json import dumps
from typing import Optional
from urllib.parse import urlencode

# Local imports
from fitbit_client.utils.types import FormDataDict
from fitbit_client.utils.types import JSONDict
from fitbit_client.utils.types import ParamDict


class CurlDebugMixin:
    """Mixin that provides curl command generation for debugging API requests.

    This mixin can be used with API client classes to add the ability to generate
    equivalent curl commands for debugging purposes. It helps with:
    - Testing API endpoints directly
    - Debugging authentication/scope issues
    - Verifying request structure
    - Troubleshooting permission problems
    """

    def _build_curl_command(
        self,
        url: str,
        http_method: str,
        data: Optional[FormDataDict] = None,
        json: Optional[JSONDict] = None,
        params: Optional[ParamDict] = None,
    ) -> str:
        """
        Build a curl command string for debugging API requests.
        
        WARNING: Security Risk - The generated command includes the actual OAuth bearer token,
        which should never be logged, shared, or committed to version control.
        See docs/SECURITY.md for guidance on securely using this feature.
        
        Args:
            url: Full API URL
            http_method: HTTP method (GET, POST, DELETE)
            data: Optional form data for POST requests
            json: Optional JSON data for POST requests
            params: Optional query parameters for GET requests
            
        Returns:
            Complete curl command as a multi-line string

        The generated command includes:
        - The HTTP method (for non-GET requests)
        - Authorization header with OAuth token (SENSITIVE INFORMATION)
        - Request body (if data or json is provided)
        - Query parameters (if provided)
        
        The command is formatted with line continuations for readability and
        can be copied directly into a terminal for testing.

        Example output:
            curl \\
              -X POST \\
              -H "Authorization: Bearer <token>" \\
              -H "Content-Type: application/json" \\
              -d '{"name": "value"}' \\
              'https://api.fitbit.com/1/user/-/foods/log.json'
        """
        # Start with base command
        cmd_parts = ["curl -v"]

        # Add method
        if http_method != "GET":
            cmd_parts.append(f"-X {http_method}")

        # Add auth header
        if hasattr(self, "oauth") and hasattr(self.oauth, "token"):
            cmd_parts.append(f'-H "Authorization: Bearer {self.oauth.token["access_token"]}"')
        else:
            # Fallback for tests or when not properly initialized
            cmd_parts.append('-H "Authorization: Bearer TOKEN"')

        # Add data if present
        if json:
            cmd_parts.append(f"-d '{dumps(json)}'")
            cmd_parts.append('-H "Content-Type: application/json"')
        elif data:
            cmd_parts.append(f"-d '{urlencode(data)}'")
            cmd_parts.append('-H "Content-Type: application/x-www-form-urlencoded"')

        # Add URL with parameters if present
        if params:
            url = f"{url}?{urlencode(params)}"
        cmd_parts.append(f"'{url}'")

        return " \\\n  ".join(cmd_parts)
