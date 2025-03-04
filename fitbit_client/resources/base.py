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
from typing import cast
from typing import overload
from urllib.parse import urlencode

# Third party imports
from requests import Response
from requests_oauthlib import OAuth2Session

# Local imports
from fitbit_client.exceptions import ERROR_TYPE_EXCEPTIONS
from fitbit_client.exceptions import FitbitAPIException
from fitbit_client.exceptions import STATUS_CODE_EXCEPTIONS
from fitbit_client.utils.curl_debug_mixin import CurlDebugMixin
from fitbit_client.utils.types import FormDataDict
from fitbit_client.utils.types import JSONDict
from fitbit_client.utils.types import JSONList
from fitbit_client.utils.types import JSONType
from fitbit_client.utils.types import ParamDict

# Constants for important fields to track in logging
IMPORTANT_RESPONSE_FIELDS: Set[str] = {
    "access",
    "date",
    "dateTime",
    "deviceId",
    "endTime",
    "foodId",
    "id",
    "logId",
    "mealTypeId",
    "name",
    "startTime",
    "subscriptionId",
    "unitId",
}


class BaseResource(CurlDebugMixin):
    """Provides foundational functionality for all Fitbit API resource classes.

    The BaseResource class implements core functionality that all specific resource
    classes (Activity, Sleep, User, etc.) inherit. It handles API communication,
    authentication, error handling, URL construction, logging, and debugging support.

    API Reference: https://dev.fitbit.com/build/reference/web-api/

    The Fitbit API has two types of endpoints:
    1. Public endpoints: /{endpoint}
       Used for database-wide operations like food search
    2. User endpoints: /user/{user_id}/{endpoint}
       Used for user-specific operations like logging activities and food.

    This base class provides:
     - URL construction for both endpoint types
     - Request handling with comprehensive error management
     - Response parsing with type safety
     - Detailed logging of requests, responses, and errors
     - Debug capabilities for API troubleshooting (via CurlDebugMixin)
     - OAuth2 authentication management

    Note:
        All resource-specific classes inherit from this class and use its _make_request
        method to communicate with the Fitbit API. The class handles different response
        formats (JSON, XML), empty responses, and various error conditions automatically.
    """

    API_BASE: str = "https://api.fitbit.com"

    def __init__(self, oauth_session: OAuth2Session, locale: str, language: str) -> None:
        """Initialize a new resource instance with authentication and locale settings.

        Args:
            oauth_session: Authenticated OAuth2 session for API requests
            locale: Locale for API responses (e.g., 'en_US')
            language: Language for API responses (e.g., 'en_US')

        The locale and language settings affect how the Fitbit API formats responses,
        particularly for things like:
        - Date and time formats
        - Measurement units (imperial vs metric)
        - Number formats (decimal separator, thousands separator)
        - Currency symbols and formats

        These settings are passed with each request in the Accept-Locale and
        Accept-Language headers.
        """
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
        """Constructs a complete Fitbit API URL for the specified endpoint.

        This method handles both public endpoints (database-wide operations) and
        user-specific endpoints (operations on user data) by constructing the
        appropriate URL pattern.

        Args:
            endpoint: API endpoint path (e.g., 'foods/log')
            user_id: User ID, defaults to '-' for authenticated user
            requires_user_id: Whether the endpoint requires user_id in the path
            api_version: API version to use (default: "1")

        Returns:
            str: Complete API URL for the requested endpoint

        Example URLs:
            User endpoint: https://api.fitbit.com/1/user/-/foods/log.json
            Public endpoint: https://api.fitbit.com/1/foods/search.json

        Note:
            By default, endpoints are assumed to be user-specific. Set requires_user_id=False
            for public endpoints that operate on Fitbit's global database rather than
            user-specific data. The user_id parameter is ignored when requires_user_id is False.

            The special user_id value "-" indicates the currently authenticated user.
        """
        endpoint = endpoint.strip("/")
        if requires_user_id:
            return f"{self.API_BASE}/{api_version}/user/{user_id}/{endpoint}"
        return f"{self.API_BASE}/{api_version}/{endpoint}"

    def _extract_important_fields(self, data: JSONDict) -> Dict[str, JSONType]:
        """
        Extract important fields from response data for logging.

        Args:
            data: Response data dictionary

        Returns:
            Dictionary containing only the important fields and their values

        This method recursively searches through the response data for fields
        defined in IMPORTANT_RESPONSE_FIELDS, preserving their path in the
        response structure using dot notation.
        """
        extracted = {}

        def extract_recursive(d: JSONDict, prefix: str = "") -> None:
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
        """
        Get the name of the method that called _make_request.

        Returns:
            Name of the calling method

        This method walks up the call stack to find the first method that isn't
        one of our internal request handling methods.
        """
        frame = currentframe()
        while frame:
            # Skip our internal methods when looking for the caller
            if frame.f_code.co_name not in (
                "_make_request",
                "_get_calling_method",
                "_handle_error_response",
            ):
                return frame.f_code.co_name
            frame = frame.f_back
        return "unknown"

    def _log_response(
        self, calling_method: str, endpoint: str, response: Response, content: Optional[Dict] = None
    ) -> None:
        """
        Handle logging for both success and error responses.

        Args:
            calling_method: Name of the method that made the request
            endpoint: API endpoint that was called
            response: Response object from the request
            content: Optional parsed response content

        This method logs both successful and failed requests with appropriate
        detail levels. For errors, it includes error types and messages when
        available.
        """
        if response.status_code >= 400:
            if isinstance(content, dict) and "errors" in content:
                error = content["errors"][0]
                msg = (
                    f"Request failed for {endpoint} "
                    f"(method: {calling_method}, status: {response.status_code}): "
                    f"[{error['errorType']}] "
                )
                if "fieldName" in error:
                    msg += f"{error['fieldName']}: {error['message']}"
                else:
                    msg += f"{error['message']}"
                self.logger.error(msg)
            else:
                self.logger.error(
                    f"Request failed for {endpoint} "
                    f"(method: {calling_method}, status: {response.status_code})"
                )
        else:
            self.logger.info(
                f"{calling_method} succeeded for {endpoint} (status {response.status_code})"
            )

    def _log_data(self, calling_method: str, content: Dict) -> None:
        """
        Log important fields from the response content.

        Args:
            calling_method: Name of the method that made the request
            content: Response content to log

        This method extracts and logs important fields from successful responses,
        creating a structured log entry with timestamp and context.
        """
        important_fields = self._extract_important_fields(content)
        if important_fields:
            data_entry = {
                "timestamp": datetime.now().isoformat(),
                "method": calling_method,
                "fields": important_fields,
            }
            self.data_logger.info(dumps(data_entry))

    def _handle_json_response(
        self, calling_method: str, endpoint: str, response: Response
    ) -> JSONType:
        """
        Handle a JSON response, including parsing and logging.

        Args:
            calling_method: Name of the method that made the request
            endpoint: API endpoint that was called
            response: Response object from the request

        Returns:
            Parsed JSON response data

        Raises:
            JSONDecodeError: If the response cannot be parsed as JSON
        """
        try:
            content = response.json()
        except JSONDecodeError:
            self.logger.error(f"Invalid JSON response from {endpoint}")
            raise

        self._log_response(calling_method, endpoint, response, content)
        if isinstance(content, dict):
            self._log_data(calling_method, content)
        return cast(JSONType, content)

    def _handle_error_response(self, response: Response) -> None:
        """
        Parse error response and raise appropriate exception.

        Args:
            response: Error response from the API

        Raises:
            Appropriate exception class based on error type or status code

        This method attempts to parse the error response and raise the most
        specific exception possible based on either the API's error type or
        the HTTP status code.
        """
        try:
            error_data = response.json()
        except (JSONDecodeError, ValueError):
            error_data = {
                "errors": [
                    {
                        "errorType": "system",
                        "message": response.text or f"HTTP {response.status_code}",
                    }
                ]
            }

        error = error_data.get("errors", [{}])[0]
        error_type = error.get("errorType", "system")
        message = error.get("message", "Unknown error")
        field_name = error.get("fieldName")

        exception_class = ERROR_TYPE_EXCEPTIONS.get(
            error_type, STATUS_CODE_EXCEPTIONS.get(response.status_code, FitbitAPIException)
        )

        self.logger.error(
            f"{exception_class.__name__}: {message} "
            f"[Type: {error_type}, Status: {response.status_code}]"
            f"{f', Field: {field_name}' if field_name else ''}"
        )

        raise exception_class(
            message=message,
            status_code=response.status_code,
            error_type=error_type,
            raw_response=error_data,
            field_name=field_name,
        )

    def _make_request(
        self,
        endpoint: str,
        data: Optional[FormDataDict] = None,
        json: Optional[JSONDict] = None,
        params: Optional[ParamDict] = None,
        headers: Dict[str, str] = {},
        user_id: str = "-",
        requires_user_id: bool = True,
        http_method: str = "GET",
        api_version: str = "1",
        debug: bool = False,
    ) -> JSONType:
        """Makes a request to the Fitbit API with error handling and debugging support.

        This core method handles all API communication for the library. It constructs URLs,
        sends requests with proper authentication, processes responses, handles errors,
        and provides debugging capabilities.

        Args:
            endpoint: API endpoint path (e.g., 'activities/steps')
            data: Optional form data for POST requests
            json: Optional JSON data for POST requests
            params: Optional query parameters for GET requests
            headers: Optional dict of additional HTTP headers to add to the request
            user_id: User ID, defaults to '-' for authenticated user
            requires_user_id: Whether the endpoint requires user_id in the path
            http_method: HTTP method to use (GET, POST, DELETE)
            api_version: API version to use (default: "1")
            debug: If True, prints a curl command to stdout to help with debugging

        Returns:
            JSONType: The API response in one of these formats:
                - JSONDict: For most JSON object responses
                - List[Any]: For endpoints that return JSON arrays
                - str: For XML/TCX responses
                - None: For successful DELETE operations or debug mode

        Raises:
            fitbit_client.exceptions.FitbitAPIException: Base class for all Fitbit API exceptions
            fitbit_client.exceptions.AuthorizationException: When there are authorization errors
            fitbit_client.exceptions.ExpiredTokenException: When the OAuth token has expired
            fitbit_client.exceptions.InsufficientPermissionsException: When the app lacks required permissions
            fitbit_client.exceptions.NotFoundException: When the requested resource doesn't exist
            fitbit_client.exceptions.RateLimitExceededException: When rate limits are exceeded
            fitbit_client.exceptions.ValidationException: When request parameters are invalid
            fitbit_client.exceptions.SystemException: When there are server-side errors

        Note:
            Debug Mode functionality:
            When debug=True, this method prints a curl command to stdout that can
            be used to replicate the request manually, which is useful for:
            - Testing API endpoints directly
            - Debugging authentication/scope issues
            - Verifying request structure
            - Troubleshooting permission problems

            The method automatically handles different response formats and appropriate
            error types based on the API's response.
        """
        calling_method = self._get_calling_method()
        url = self._build_url(endpoint, user_id, requires_user_id, api_version)

        if debug:
            curl_command = self._build_curl_command(url, http_method, data, json, params)
            print(f"\n# Debug curl command for {calling_method}:")
            print(curl_command)
            print()
            return None

        self.headers.update(headers)

        try:
            response: Response = self.oauth.request(
                http_method, url, data=data, json=json, params=params, headers=self.headers
            )

            # Handle error responses
            if response.status_code >= 400:
                self._handle_error_response(response)

            content_type = response.headers.get("content-type", "").lower()

            # Handle empty responses
            if response.status_code == 204 or not content_type:
                self.logger.info(
                    f"{calling_method} succeeded for {endpoint} (status {response.status_code})"
                )
                return None

            # Handle JSON responses
            if "application/json" in content_type:
                return self._handle_json_response(calling_method, endpoint, response)

            # Handle XML/TCX responses
            elif "application/vnd.garmin.tcx+xml" in content_type or "text/xml" in content_type:
                self._log_response(calling_method, endpoint, response)
                return cast(str, response.text)

            # Handle unexpected content types
            self.logger.error(f"Unexpected content type {content_type} for {endpoint}")
            return None

        except Exception as e:
            self.logger.error(
                f"{e.__class__.__name__} in {calling_method} for {endpoint}: {str(e)}"
            )
            raise
