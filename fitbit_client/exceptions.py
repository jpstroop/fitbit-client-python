# fitbit_client/exceptions.py

# Standard library imports
from typing import Any
from typing import Dict
from typing import List
from typing import Optional


class FitbitAPIException(Exception):
    """Base exception for all Fitbit API errors"""

    def __init__(
        self,
        message: str,
        error_type: str,
        status_code: Optional[int] = None,
        raw_response: Optional[Dict[str, Any]] = None,
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
    """Raised when the application hits rate limiting quotas"""

    pass


class SystemException(RequestException):
    """Raised when there's a system-level failure"""

    pass


class ValidationException(RequestException):
    """Raised when a request parameter is invalid or missing"""

    pass


## PreRequestValidaton Exceptions


class ClientValidationException(FitbitAPIException):
    """Superclass for validations that take place before making a request"""

    def __init__(
        self,
        message: str,
        error_type: str = "client_validation",
        field_name: Optional[str] = None,
        raw_response: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_type=error_type,
            status_code=None,
            raw_response=raw_response,
            field_name=field_name,
        )


class InvalidDateException(ClientValidationException):
    """Raised when a date string is not in the correct format or not a valid calendar date"""

    def __init__(
        self, date_str: str, field_name: Optional[str] = None, message: Optional[str] = None
    ):
        super().__init__(
            message=message or f"Invalid date format. Expected YYYY-MM-DD, got: {date_str}",
            error_type="invalid_date",
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
        # Use the provided reason directly - don't override it
        message = f"Invalid date range: {reason}"

        super().__init__(message=message, error_type="invalid_date_range", field_name="date_range")
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
        super().__init__(message=message, error_type="pagination", field_name=field_name)


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

        super().__init__(message=error_msg, field_name=field_name, error_type="intraday_validation")
        self.allowed_values = allowed_values
        self.resource_name = resource_name


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
