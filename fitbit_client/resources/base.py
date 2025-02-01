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

    API_BASE: str = "https://api.fitbit.com"

    def __init__(self, oauth_session: OAuth2Session, locale: str, language: str) -> None:
        self.headers: Dict = {"Accept-Locale": locale, "Accept-Language": language}
        self.oauth: OAuth2Session = oauth_session
        # Initialize loggers
        self.logger = getLogger(f"fitbit_client.{self.__class__.__name__}")
        self.data_logger = getLogger("fitbit_client.data")

    def _build_url(
        self,
        endpoint: str,
        user_id: str = "-",
        requires_user_id: bool = True,
        api_version: str = "1",
    ) -> str:
        """
        Build full API URL with support for both public and user-specific endpoints.

        By default, endpoints are assumed to be user-specific. Set requires_user_id=False
        for public endpoints that operate on Fitbit's global database rather than
        user-specific data.

        Parameters:
            endpoint: API endpoint path
            user_id: User ID, defaults to '-' for authenticated user
            requires_user_id: Whether the endpoint requires user_id in the path
            api_version: API version to use (default: "1")

        Returns:
            Complete API URL
        """
        endpoint = endpoint.strip("/")
        if requires_user_id:
            return f"{self.API_BASE}/{api_version}/user/{user_id}/{endpoint}"
        return f"{self.API_BASE}/{api_version}/{endpoint}"

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

    def _get_calling_method(self) -> str:
        """Get the name of the method that called _make_request."""
        frame = currentframe()
        while frame:
            if frame.f_code.co_name != "_make_request":
                return frame.f_code.co_name
            frame = frame.f_back
        return "unknown"

    def _log_response(
        self, calling_method: str, endpoint: str, response: Response, content: Optional[Dict] = None
    ) -> None:
        """Handle logging for both success and error responses."""
        if response.status_code >= 400:
            if isinstance(content, dict) and "errors" in content:
                error = content["errors"][0]
                msg = f"Request failed for {endpoint} (status {response.status_code}): "
                if "fieldName" in error:
                    msg += f"[{error['errorType']}] {error['fieldName']}: {error['message']}"
                else:
                    msg += f"[{error['errorType']}] {error['message']}"
                self.logger.error(msg)
            else:
                self.logger.error(f"Request failed for {endpoint} (status {response.status_code})")
        else:
            self.logger.info(
                f"{calling_method} succeeded for {endpoint} (status {response.status_code})"
            )

    def _log_data(self, calling_method: str, content: Dict) -> None:
        """Log important fields from the response content."""
        important_fields = self._extract_important_fields(content)
        if important_fields:
            data_entry = {
                "timestamp": datetime.now().isoformat(),
                "method": calling_method,
                "fields": important_fields,
            }
            self.data_logger.info(dumps(data_entry))

    def _handle_json_response(self, calling_method: str, endpoint: str, response: Response) -> Dict:
        """Handle a JSON response, including parsing and logging."""
        try:
            content = response.json()
        except JSONDecodeError:
            self.logger.error(f"Invalid JSON response from {endpoint}")
            raise

        self._log_response(calling_method, endpoint, response, content)
        if isinstance(content, dict):
            self._log_data(calling_method, content)
        return content

    def _make_request(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        user_id: str = "-",
        requires_user_id: bool = True,
        http_method: str = "GET",
        api_version: str = "1",
    ) -> Any:
        """
        Make a request to Fitbit API

        Parameters:
            endpoint: API endpoint path
            data: Optional form data
            json: Optional JSON data
            params: Optional query parameters
            user_id: User ID, defaults to '-' for authenticated user
            requires_user_id: Whether the endpoint is user-specific (default: True)
            http_method: GET (default), POST, or DELETE
            api_version: API version to use (default: "1")

        Returns:
            The API response content (typically Dict[str, Any] or None for DELETE)
        """
        calling_method = self._get_calling_method()
        url = self._build_url(endpoint, user_id, requires_user_id, api_version)

        try:
            response: Response = self.oauth.request(
                http_method, url, data=data, json=json, params=params, headers=self.headers
            )

            if response.status_code >= 500:
                self.logger.error(f"Server error for {endpoint} (status {response.status_code})")
                raise HTTPError(response=response)

            content_type = response.headers.get("content-type", "").lower()

            if response.status_code == 204 or not content_type:
                self.logger.info(
                    f"{calling_method} succeeded for {endpoint} (status {response.status_code})"
                )
                return None

            if "application/json" in content_type:
                return self._handle_json_response(calling_method, endpoint, response)

            elif "application/vnd.garmin.tcx+xml" in content_type or "text/xml" in content_type:
                self._log_response(calling_method, endpoint, response)
                return response.text

            self.logger.error(f"Unexpected content type {content_type} for {endpoint}")
            return response.text

        except Exception as e:
            self.logger.exception(f"Unexpected error in {calling_method} for {endpoint}: {str(e)}")
            raise
