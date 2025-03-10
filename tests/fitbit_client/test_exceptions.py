# tests/fitbit_client/test_exceptions.py

# Standard library imports
from typing import List
from typing import Union

# Third party imports
from pytest import mark

# Local imports
from fitbit_client.exceptions import AuthorizationException
from fitbit_client.exceptions import ClientValidationException
from fitbit_client.exceptions import ERROR_TYPE_EXCEPTIONS
from fitbit_client.exceptions import ExpiredTokenException
from fitbit_client.exceptions import FitbitAPIException
from fitbit_client.exceptions import InsufficientPermissionsException
from fitbit_client.exceptions import InsufficientScopeException
from fitbit_client.exceptions import IntradayValidationException
from fitbit_client.exceptions import InvalidClientException
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException
from fitbit_client.exceptions import InvalidGrantException
from fitbit_client.exceptions import InvalidRequestException
from fitbit_client.exceptions import InvalidTokenException
from fitbit_client.exceptions import MissingParameterException
from fitbit_client.exceptions import NotFoundException
from fitbit_client.exceptions import OAuthException
from fitbit_client.exceptions import ParameterValidationException
from fitbit_client.exceptions import RateLimitExceededException
from fitbit_client.exceptions import RequestException
from fitbit_client.exceptions import STATUS_CODE_EXCEPTIONS
from fitbit_client.exceptions import SystemException
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.constants import IntradayDetailLevel


class TestBaseException:
    """Test the base FitbitAPIException"""

    def test_base_exception_minimal(self):
        """Test creating base exception with minimal parameters"""
        exc = FitbitAPIException(message="Test error", error_type="test")
        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.error_type == "test"
        assert exc.status_code is None
        assert exc.raw_response is None
        assert exc.field_name is None

    def test_base_exception_full(self):
        """Test creating base exception with all parameters"""
        raw_response = {"errors": [{"message": "Test error"}]}
        exc = FitbitAPIException(
            message="Test error",
            error_type="test",
            status_code=400,
            raw_response=raw_response,
            field_name="test_field",
        )
        assert exc.message == "Test error"
        assert exc.error_type == "test"
        assert exc.status_code == 400
        assert exc.raw_response == raw_response
        assert exc.field_name == "test_field"


class TestOAuthExceptions:
    """Test OAuth-related exceptions"""

    @mark.parametrize(
        "exc_class",
        [
            OAuthException,
            ExpiredTokenException,
            InvalidGrantException,
            InvalidTokenException,
            InvalidClientException,
        ],
    )
    def test_oauth_exceptions(self, exc_class):
        """Test all OAuth exception classes"""
        exc = exc_class(message="OAuth error", error_type="oauth", status_code=401)
        assert isinstance(exc, OAuthException)
        assert isinstance(exc, FitbitAPIException)
        assert str(exc) == "OAuth error"
        assert exc.status_code == 401


class TestRequestExceptions:
    """Test request-related exceptions"""

    @mark.parametrize(
        "exc_class",
        [
            RequestException,
            InvalidRequestException,
            AuthorizationException,
            InsufficientPermissionsException,
            InsufficientScopeException,
            NotFoundException,
            RateLimitExceededException,
            SystemException,
            ValidationException,
        ],
    )
    def test_request_exceptions(self, exc_class):
        """Test all request exception classes"""
        exc = exc_class(message="Request error", error_type="request", status_code=400)
        assert isinstance(exc, RequestException)
        assert isinstance(exc, FitbitAPIException)
        assert str(exc) == "Request error"
        assert exc.status_code == 400


class TestValidationExceptions:
    """Test validation exceptions"""

    def test_invalid_date_exception_minimal(self):
        """Test InvalidDateException with minimal parameters"""
        exc = InvalidDateException(date_str="2024-13-45")
        assert isinstance(exc, ClientValidationException)
        assert "Invalid date format" in str(exc)
        assert exc.date_str == "2024-13-45"
        assert exc.field_name is None

    def test_invalid_date_exception_full(self):
        """Test InvalidDateException with all parameters"""
        exc = InvalidDateException(
            date_str="2024-13-45", field_name="test_date", message="Custom error message"
        )
        assert str(exc) == "Custom error message"
        assert exc.date_str == "2024-13-45"
        assert exc.field_name == "test_date"

    def test_invalid_date_range_exception_minimal(self):
        """Test InvalidDateRangeException with minimal parameters"""
        exc = InvalidDateRangeException(
            start_date="2024-01-01", end_date="2023-12-31", reason="End date before start date"
        )
        assert isinstance(exc, ClientValidationException)
        assert "Invalid date range" in str(exc)
        assert "End date before start date" in str(exc)
        assert exc.start_date == "2024-01-01"
        assert exc.end_date == "2023-12-31"
        assert exc.max_days is None
        assert exc.resource_name is None

    def test_invalid_date_range_exception_full(self):
        """Test InvalidDateRangeException with all parameters"""
        exc = InvalidDateRangeException(
            start_date="2024-01-01",
            end_date="2024-02-01",
            reason="Exceeds maximum days",
            max_days=30,
            resource_name="activity",
        )
        assert "Invalid date range" in str(exc)
        assert "Exceeds maximum days" in str(exc)
        assert exc.max_days == 30
        assert exc.resource_name == "activity"


class TestIntradayValidationException:
    """Test suite for IntradayValidationException"""

    def test_intraday_validation_exception_minimal(self):
        """Test with minimal required parameters"""
        exc = IntradayValidationException(message="Invalid parameter", field_name="detail_level")
        assert isinstance(exc, ClientValidationException)
        assert str(exc) == "Invalid parameter"
        assert exc.field_name == "detail_level"
        assert exc.allowed_values is None
        assert exc.resource_name is None

    def test_intraday_validation_exception_with_enums(self):
        """Test IntradayValidationException with enum values"""
        exc = IntradayValidationException(
            message="Invalid detail level",
            field_name="detail_level",
            allowed_values=[
                IntradayDetailLevel.FIFTEEN_MINUTES.value,
                IntradayDetailLevel.ONE_SECOND.value,
                IntradayDetailLevel.FIVE_MINUTES.value,
                IntradayDetailLevel.ONE_MINUTE.value,
            ],
            resource_name="heart rate",
        )
        # Just verify each value is in the message
        assert all(
            val.value in str(exc)
            for val in [
                IntradayDetailLevel.ONE_SECOND,
                IntradayDetailLevel.ONE_MINUTE,
                IntradayDetailLevel.FIVE_MINUTES,
                IntradayDetailLevel.FIFTEEN_MINUTES,
            ]
        )

    def test_intraday_validation_mixed_values(self):
        """Test handling mix of enum values and strings"""
        values: List[Union[str, IntradayDetailLevel]] = [
            IntradayDetailLevel.FIFTEEN_MINUTES,
            "1sec",
            IntradayDetailLevel.ONE_MINUTE,
        ]  # Raw string
        exc = IntradayValidationException(
            message="Invalid detail level",
            field_name="detail_level",
            allowed_values=values,
            resource_name="heart rate",
        )
        assert all(
            val.value in str(exc)
            for val in [
                IntradayDetailLevel.ONE_SECOND,
                IntradayDetailLevel.ONE_MINUTE,
                IntradayDetailLevel.FIVE_MINUTES,
                IntradayDetailLevel.FIFTEEN_MINUTES,
            ]
        )

    def test_intraday_validation_full_enum_values(self):
        """Test with all IntradayDetailLevel enum values"""
        exc = IntradayValidationException(
            message="Invalid detail level",
            field_name="detail_level",
            allowed_values=list(IntradayDetailLevel),
            resource_name="heart rate",
        )
        assert all(
            val.value in str(exc)
            for val in [
                IntradayDetailLevel.ONE_SECOND,
                IntradayDetailLevel.ONE_MINUTE,
                IntradayDetailLevel.FIVE_MINUTES,
                IntradayDetailLevel.FIFTEEN_MINUTES,
            ]
        )

    def test_intraday_validation_exception_with_resource(self):
        """Test error message formatting with resource name"""
        exc = IntradayValidationException(
            message="Invalid detail level",
            field_name="detail_level",
            allowed_values=[IntradayDetailLevel.ONE_MINUTE],
            resource_name="heart rate",
        )
        assert str(exc) == "Invalid detail level. Allowed values: 1min for heart rate"


class TestParameterValidationException:
    """Test suite for ParameterValidationException"""

    def test_parameter_validation_exception_minimal(self):
        """Test with minimal required parameters"""
        exc = ParameterValidationException(message="Value must be positive")
        assert isinstance(exc, ClientValidationException)
        assert str(exc) == "Value must be positive"
        assert exc.field_name is None

    def test_parameter_validation_exception_with_field(self):
        """Test with field name specified"""
        exc = ParameterValidationException(message="Value must be positive", field_name="duration")
        assert str(exc) == "Value must be positive"
        assert exc.field_name == "duration"


class TestMissingParameterException:
    """Test suite for MissingParameterException"""

    def test_missing_parameter_exception_minimal(self):
        """Test with minimal required parameters"""
        exc = MissingParameterException(message="Required parameter missing")
        assert isinstance(exc, ClientValidationException)
        assert str(exc) == "Required parameter missing"
        assert exc.field_name is None

    def test_missing_parameter_exception_with_field(self):
        """Test with field name specified"""
        exc = MissingParameterException(
            message="Must provide either food_id or food_name", field_name="food_parameter"
        )
        assert str(exc) == "Must provide either food_id or food_name"
        assert exc.field_name == "food_parameter"


class TestExceptionMappings:
    """Test exception mapping dictionaries"""

    @mark.parametrize(
        "status_code,expected_class",
        [
            (400, InvalidRequestException),
            (401, AuthorizationException),
            (403, InsufficientPermissionsException),
            (404, NotFoundException),
            (409, InvalidRequestException),
            (429, RateLimitExceededException),
            (500, SystemException),
            (502, SystemException),
            (503, SystemException),
            (504, SystemException),
        ],
    )
    def test_status_code_mapping(self, status_code: int, expected_class: type):
        """Test that status codes map to correct exception classes"""
        assert STATUS_CODE_EXCEPTIONS[status_code] == expected_class

    @mark.parametrize(
        "error_type,expected_class",
        [
            ("authorization", AuthorizationException),
            ("expired_token", ExpiredTokenException),
            ("insufficient_permissions", InsufficientPermissionsException),
            ("insufficient_scope", InsufficientScopeException),
            ("invalid_client", InvalidClientException),
            ("invalid_grant", InvalidGrantException),
            ("invalid_request", InvalidRequestException),
            ("invalid_token", InvalidTokenException),
            ("not_found", NotFoundException),
            ("oauth", OAuthException),
            ("request", RequestException),
            ("system", SystemException),
            ("validation", ValidationException),
        ],
    )
    def test_error_type_mapping(self, error_type: str, expected_class: type):
        """Test that error types map to correct exception classes"""
        assert ERROR_TYPE_EXCEPTIONS[error_type] == expected_class
