# fitbit_client/exceptions.py

# Standard library imports
from typing import Any
from typing import Dict
from typing import Optional


class FitbitAPIException(Exception):
    """Base exception for all Fitbit API errors"""

    def __init__(
        self,
        message: str,
        status_code: int,
        error_type: str,
        raw_response: Optional[Dict[str, Any]] = None,
        field_name: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        self.raw_response = raw_response
        self.field_name = field_name
        super().__init__(self.message)


class AuthorizationException(FitbitAPIException):
    """Raised when there are authorization-related errors"""

    pass


class ExpiredTokenException(FitbitAPIException):
    """Raised when the OAuth token has expired"""

    pass


class InsufficientPermissionsException(FitbitAPIException):
    """Raised when the application has insufficient permissions"""

    pass


class InsufficientScopeException(FitbitAPIException):
    """Raised when the application is missing a required scope"""

    pass


class InvalidClientException(FitbitAPIException):
    """Raised when the client_id is invalid"""

    pass


class InvalidGrantException(FitbitAPIException):
    """Raised when the grant_type value is invalid"""

    pass


class InvalidRequestException(FitbitAPIException):
    """Raised when the request syntax is invalid"""

    pass


class InvalidScopeException(FitbitAPIException):
    """Raised when the scope is invalid"""

    pass


class InvalidTokenException(FitbitAPIException):
    """Raised when the OAuth token is invalid"""

    pass


class NotFoundException(FitbitAPIException):
    """Raised when the requested resource doesn't exist"""

    pass


class OAuthException(FitbitAPIException):
    """Raised when OAuth token is invalid, missing or expired"""

    pass


class RateLimitExceededException(FitbitAPIException):
    """Raised when the application hits rate limiting quotas"""

    pass


class RequestException(FitbitAPIException):
    """Raised when the API request fails"""

    pass


class SystemException(FitbitAPIException):
    """Raised when there's a system-level failure"""

    pass


class ValidationException(FitbitAPIException):
    """Raised when a request parameter is invalid or missing"""

    pass


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

# Map error types to exception classes
ERROR_TYPE_EXCEPTIONS = {
    "authorization": AuthorizationException,
    "expired_token": ExpiredTokenException,
    "insufficient_permissions": InsufficientPermissionsException,
    "insufficient_scope": InsufficientScopeException,
    "invalid_client": InvalidClientException,
    "invalid_grant": InvalidGrantException,
    "invalid_request": InvalidRequestException,
    "invalid_scope": InvalidScopeException,
    "invalid_token": InvalidTokenException,
    "not_found": NotFoundException,
    "oauth": OAuthException,
    "request": RequestException,
    "system": SystemException,
    "validation": ValidationException,
}
