# fitbit_client/exceptions.py

# Standard library imports
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from requests import Response

# Local imports
from fitbit_client.utils.types import JSONDict


class FitbitAPIException(Exception):
    """Base exception for all Fitbit API errors"""

    def __init__(
        self,
        message: str,
        error_type: str,
        status_code: Optional[int] = None,
        raw_response: Optional[JSONDict] = None,
        field_name: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        self.raw_response = raw_response
        self.field_name = field_name
        super().__init__(self.message)


## OAuthExceptions


class OAuthException(FitbitAPIException):
    """Superclass for all authentication flow exceptions"""

    pass


class ExpiredTokenException(OAuthException):
    """Raised when the OAuth token has expired"""

    pass


class InvalidGrantException(OAuthException):
    """Raised when the grant_type value is invalid"""

    pass


class InvalidTokenException(OAuthException):
    """Raised when the OAuth token is invalid"""

    pass


class InvalidClientException(OAuthException):
    """Raised when the client_id is invalid"""

    pass


##  Request Exceptions


class RequestException(FitbitAPIException):
    """Superclass for all API request exceptions"""

    pass


class InvalidRequestException(RequestException):
    """Raised when the request syntax is invalid"""

    pass


class AuthorizationException(RequestException):
    """Raised when there are authorization-related errors"""

    pass


class InsufficientPermissionsException(RequestException):
    """Raised when the application has insufficient permissions"""

    pass


class InsufficientScopeException(RequestException):
    """Raised when the application is missing a required scope"""

    pass


class NotFoundException(RequestException):
    """Raised when the requested resource does not exist"""

    pass


class RateLimitExceededException(RequestException):
    """Raised when the application hits rate limiting quotas.

    The Fitbit API enforces a limit of 150 API calls per hour per user.
    When this limit is reached, the API returns a 429 status code, with
    headers indicating the limit, remaining calls, and seconds until reset.

    Attributes:
        message: Human-readable error message
        status_code: HTTP status code (429)
        error_type: The API error type ("rate_limit_exceeded")
        raw_response: Raw response from the API
        field_name: Optional field name associated with the error
        rate_limit: The total number of allowed calls (usually 150)
        rate_limit_remaining: The number of calls remaining before hitting the limit
        rate_limit_reset: The number of seconds until the rate limit resets
        response: The original response object (for retry logic)
    """

    def __init__(
        self,
        message: str,
        error_type: str,
        status_code: Optional[int] = None,
        raw_response: Optional[JSONDict] = None,
        field_name: Optional[str] = None,
        rate_limit: Optional[int] = None,
        rate_limit_remaining: Optional[int] = None,
        rate_limit_reset: Optional[int] = None,
        response: Optional["Response"] = None,
    ):
        super().__init__(
            message=message,
            error_type=error_type,
            status_code=status_code,
            raw_response=raw_response,
            field_name=field_name,
        )
        self.rate_limit = rate_limit
        self.rate_limit_remaining = rate_limit_remaining
        self.rate_limit_reset = rate_limit_reset
        self.response = response


class SystemException(RequestException):
    """Raised when there's a system-level failure"""

    pass


class ValidationException(RequestException):
    """Raised when a request parameter is invalid or missing"""

    pass


## PreRequestValidaton Exceptions


class ClientValidationException(ValueError):
    """Superclass for validations that take place before making any API request.

    These exceptions indicate that input validation failed locally, without making
    any network requests. This helps preserve API rate limits and gives more specific
    error information than would be available from the API response."""

    def __init__(self, message: str, field_name: Optional[str] = None):
        """Initialize client validation exception.

        Args:
            message: Human-readable error message
            field_name: Optional name of the invalid field
        """
        self.message = message
        self.field_name = field_name
        super().__init__(self.message)


class InvalidDateException(ClientValidationException):
    """Raised when a date string is not in the correct format or not a valid calendar date"""

    def __init__(
        self, date_str: str, field_name: Optional[str] = None, message: Optional[str] = None
    ):
        """Initialize invalid date exception.

        Args:
            date_str: The invalid date string
            field_name: Optional name of the date field
            message: Optional custom error message. If not provided, a default message is generated.
        """
        super().__init__(
            message=message or f"Invalid date format. Expected YYYY-MM-DD, got: {date_str}",
            field_name=field_name,
        )
        self.date_str = date_str


class InvalidDateRangeException(ClientValidationException):
    """Raised when a date range is invalid (e.g., end before start, exceeds max days)"""

    def __init__(
        self,
        start_date: str,
        end_date: str,
        reason: str,
        max_days: Optional[int] = None,
        resource_name: Optional[str] = None,
    ):
        """Initialize invalid date range exception.

        Args:
            start_date: The start date of the invalid range
            end_date: The end date of the invalid range
            reason: Specific reason why the date range is invalid
            max_days: Optional maximum number of days allowed for this request
            resource_name: Optional resource or endpoint name for context
        """
        # Use the provided reason directly - don't override it
        message = f"Invalid date range: {reason}"

        super().__init__(message=message, field_name="date_range")
        self.start_date = start_date
        self.end_date = end_date
        self.max_days = max_days
        self.resource_name = resource_name


class PaginationException(ClientValidationException):
    """Raised when pagination-related parameters are invalid"""

    def __init__(self, message: str, field_name: Optional[str] = None):
        """Initialize pagination validation exception

        Args:
            message: Error message describing the validation failure
            field_name: Optional name of the invalid field
        """
        super().__init__(message=message, field_name=field_name)


class IntradayValidationException(ClientValidationException):
    """Raised when intraday request parameters are invalid"""

    def __init__(
        self,
        message: str,
        field_name: str,
        allowed_values: Optional[List[str]] = None,
        resource_name: Optional[str] = None,
    ):
        """Initialize intraday validation exception

        Args:
            message: Error message
            field_name: Name of the invalid field
            allowed_values: Optional list of valid values
            resource_name: Optional name of the resource/endpoint
        """
        error_msg = message
        if allowed_values:
            error_msg = f"{message}. Allowed values: {', '.join(sorted(allowed_values))}"
        if resource_name:
            error_msg = f"{error_msg} for {resource_name}"

        super().__init__(message=error_msg, field_name=field_name)
        self.allowed_values = allowed_values
        self.resource_name = resource_name


class ParameterValidationException(ClientValidationException):
    """Raised when a parameter value is invalid (e.g., negative when positive required)"""

    def __init__(self, message: str, field_name: Optional[str] = None):
        """Initialize parameter validation exception

        Args:
            message: Error message describing the validation failure
            field_name: Optional name of the invalid field
        """
        super().__init__(message=message, field_name=field_name)


class MissingParameterException(ClientValidationException):
    """Raised when required parameters are missing or parameter combinations are invalid"""

    def __init__(self, message: str, field_name: Optional[str] = None):
        """Initialize missing parameter exception

        Args:
            message: Error message describing the validation failure
            field_name: Optional name of the invalid or missing field
        """
        super().__init__(message=message, field_name=field_name)


# Map HTTP status codes to exception classes
STATUS_CODE_EXCEPTIONS = {
    400: InvalidRequestException,
    401: AuthorizationException,
    403: InsufficientPermissionsException,
    404: NotFoundException,
    409: InvalidRequestException,
    429: RateLimitExceededException,
    500: SystemException,
    502: SystemException,
    503: SystemException,
    504: SystemException,
}

# Map fitbit error types to exception classes. The keys match the `errorType`s listed here:
# https://dev.fitbit.com/build/reference/web-api/troubleshooting-guide/error-handling/#types-of-errors
# This is elegant and efficient, but may take some time to understand!
ERROR_TYPE_EXCEPTIONS = {
    "authorization": AuthorizationException,
    "expired_token": ExpiredTokenException,
    "insufficient_permissions": InsufficientPermissionsException,
    "insufficient_scope": InsufficientScopeException,
    "invalid_client": InvalidClientException,
    "invalid_grant": InvalidGrantException,
    "invalid_request": InvalidRequestException,
    "invalid_token": InvalidTokenException,
    "not_found": NotFoundException,
    "oauth": OAuthException,
    "request": RequestException,
    "system": SystemException,
    "validation": ValidationException,
}
