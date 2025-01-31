# fitbit_client/resources/base.py

# Standard library imports
from datetime import datetime
from inspect import currentframe
from json import JSONDecodeError
from json import dumps
from logging import getLogger
from typing import Any
from typing import Dict
from typing import Optional
from typing import Set

# Third party imports
from requests import HTTPError
from requests import Response
from requests_oauthlib import OAuth2Session

# Constants for important fields to track in logging
IMPORTANT_RESPONSE_FIELDS: Set[str] = {
    "access",  # PUBLIC/PRIVATE/SHARED
    "date",  # Dates
    "dateTime",  # Timestamps
    "deviceId",  # Device IDs
    "endTime",  # Activity/sleep end times
    "foodId",  # Food resource IDs
    "id",  # Generic resource IDs
    "logId",  # Log entry IDs
    "mealTypeId",  # Type of Meal
    "name",  # Resource names
    "startTime",  # Activity/sleep start times
    "subscriptionId",  # Subscription IDs
    "unitId",  # Measurement unit IDs
}


class BaseResource:
    """
    Base class for all Fitbit API resources

    The Fitbit API has two types of endpoints:
    1. Public endpoints: /{endpoint}
       Used for database-wide operations like food search
    2. User endpoints: /user/{user_id}/{endpoint}
       Used for user-specific operations like logging food
    """

    API_BASE: str = "https://api.fitbit.com/1"

    def __init__(self, oauth_session: OAuth2Session, locale: str, language: str) -> None:
        self.headers: Dict = {"Accept-Locale": locale, "Accept-Language": language}
        self.oauth: OAuth2Session = oauth_session
        # Initialize loggers
        self.logger = getLogger(f"fitbit_client.{self.__class__.__name__}")
        self.data_logger = getLogger("fitbit_client.data")

    def _build_url(self, endpoint: str, user_id: str = "-", requires_user_id: bool = True) -> str:
        """
        Build full API URL with support for both public and user-specific endpoints.

        By default, endpoints are assumed to be user-specific. Set requires_user_id=False
        for public endpoints that operate on Fitbit's global database rather than
        user-specific data.

        Parameters:
            endpoint: API endpoint path
            user_id: User ID, defaults to '-' for authenticated user
            requires_user_id: Whether the endpoint requires user_id in the path

        Returns:
            Complete API URL
        """
        endpoint = endpoint.strip("/")
        if requires_user_id:
            return f"{self.API_BASE}/user/{user_id}/{endpoint}"
        return f"{self.API_BASE}/{endpoint}"

    def _extract_important_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract important fields from response data for logging."""
        extracted = {}

        def extract_recursive(d: Dict[str, Any], prefix: str = "") -> None:
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key

                if key in IMPORTANT_RESPONSE_FIELDS:
                    extracted[full_key] = value

                if isinstance(value, dict):
                    extract_recursive(value, full_key)
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            extract_recursive(item, f"{full_key}[{i}]")

        extract_recursive(data)
        return extracted

    def _make_request(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        user_id: str = "-",
        requires_user_id: bool = True,
        http_method: str = "GET",
    ) -> Any:
        """
        Make a request to Fitbit API

        Parameters:
            endpoint: API endpoint path
            params: Optional query parameters
            data: Optional form data
            user_id: User ID, defaults to '-' for authenticated user
            requires_user_id: Whether the endpoint is user-specific (default: True)
            http_method: GET (default), POST, or DELETE

        Returns:
            The API response content (typically Dict[str, Any] or None for DELETE)
        """
        # Find the original caller by walking up the stack
        frame = currentframe()
        calling_method = "unknown"
        while frame:
            if frame.f_code.co_name != "_make_request":
                calling_method = frame.f_code.co_name
                break
            frame = frame.f_back

        url: str = self._build_url(endpoint, user_id, requires_user_id)

        try:
            # Make the request
            response: Response = self.oauth.request(
                http_method, url, data=data, json=json, params=params, headers=self.headers
            )

            # Handle error responses
            try:
                response.raise_for_status()
            except HTTPError:
                if response.status_code >= 500:
                    raise
                # Swallow client errors that might have useful response content
                # TODO: Add custom exception handling here based on Fitbit's documented error types.
                # For example, rate limiting, invalid parameters, authentication errors, etc.
                # This will allow users to catch specific types of errors instead of generic HTTP errors.
                pass

            # Parse the response
            try:
                if http_method == "DELETE":
                    content = response.text
                else:
                    content = response.json()
            except JSONDecodeError as e:
                # Brief error at ERROR level
                self.logger.error(f"Failed to decode JSON response from {endpoint}")

                # Detailed debug info
                self.logger.debug(
                    "JSON decode error details:\n"
                    f"Status: {response.status_code}\n"
                    f"Response Body: {response.text}\n"
                    f"Headers: {dict(response.headers)}"
                )

                raise JSONDecodeError(
                    f"Failed to decode response from {endpoint}", e.doc, e.pos
                ) from e

            # Log the request details
            debug_msg = (
                f"API Call Details:\n"
                f"Endpoint: {endpoint}\n"
                f"Method: {calling_method}\n"
                f"Status: {response.status_code}\n"
                f"Parameters: {params}\n"
                f"Headers: {dict(response.headers)}\n"
                f"Response: {content}"
            )
            self.logger.debug(debug_msg)

            # Log success/failure at INFO level
            # Log errors and handle specific error types
            # TODO: Add custom exception classes based on Fitbit's documented error types (rate limiting,
            # invalid parameters, authentication errors, etc). This will allow users to catch specific
            # error types rather than parsing the error response themselves.
            if (
                isinstance(content, dict)
                and "errors" in content
                and isinstance(content["errors"], list)
            ):
                error = content["errors"][0]
                msg = f"Request failed for {endpoint} (status {response.status_code}): "
                if "fieldName" in error:
                    msg += f"[{error['errorType']}] {error['fieldName']}: {error['message']}"
                else:
                    msg += f"[{error['errorType']}] {error['message']}"
                self.logger.info(msg)
                if response.status_code >= 400:
                    self.logger.error(msg)
            else:
                self.logger.info(
                    f"{calling_method} succeeded for {endpoint} (status {response.status_code})"
                )

            # Log important data fields on success
            if response.status_code < 400 and isinstance(content, dict):
                important_fields = self._extract_important_fields(content)
                if important_fields:
                    data_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "method": calling_method,
                        "fields": important_fields,
                    }
                    self.data_logger.info(dumps(data_entry))

            return content

        except Exception as e:
            self.logger.exception(f"Unexpected error in {calling_method} for {endpoint}: {str(e)}")
            raise
