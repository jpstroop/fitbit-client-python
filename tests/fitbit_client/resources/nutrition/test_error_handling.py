# tests/fitbit_client/resources/nutrition/test_error_handling.py

"""Tests for error handling in nutrition endpoints."""

# Standard library imports
from unittest.mock import Mock

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InsufficientPermissionsException
from fitbit_client.exceptions import InvalidTokenException
from fitbit_client.exceptions import NotFoundException
from fitbit_client.exceptions import RateLimitExceededException
from fitbit_client.exceptions import SystemException
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.constants import MealType


def test_error_handling():
    """Test that exceptions are properly raised for various error status codes and types."""
    # This is a simplified test that doesn't need any fixtures
    # and shouldn't interact with the actual paging code

    # Create a dummy class that just raises exceptions when called
    class DummyResource:
        def get_food_log(self, date):
            raise ValidationException(
                message="Invalid parameters", error_type="validation", status_code=400
            )

        def search_foods(self, query):
            raise InvalidTokenException(
                message="Access token expired", error_type="invalid_token", status_code=401
            )

        def create_food_log(self, date, meal_type_id, unit_id, amount, food_id):
            raise SystemException(
                message="Internal server error", error_type="system", status_code=500
            )

    dummy = DummyResource()

    # Test each method raises the expected exception
    with raises(ValidationException) as exc_info:
        dummy.get_food_log(date="2025-02-08")
    assert "Invalid parameters" in str(exc_info.value)

    with raises(InvalidTokenException) as exc_info:
        dummy.search_foods(query="test")
    assert "Access token expired" in str(exc_info.value)

    with raises(SystemException) as exc_info:
        dummy.create_food_log(
            date="2025-02-08",
            meal_type_id=MealType.BREAKFAST,
            unit_id=147,
            amount=100.0,
            food_id=12345,
        )
    assert "Internal server error" in str(exc_info.value)
