# tests/resources/nutrition/test_error_handling.py

"""Tests for the error_handling endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.resources.constants import MealType


def test_error_handling(nutrition_resource, mock_response_factory):
    """Test error handling for various error types and status codes"""
    error_cases = [
        {
            "status_code": 400,
            "error_type": "validation",
            "message": "Invalid parameters",
            "expected_exception": "ValidationException",
        },
        {
            "status_code": 401,
            "error_type": "invalid_token",
            "message": "Access token expired",
            "expected_exception": "InvalidTokenException",
        },
        {
            "status_code": 403,
            "error_type": "insufficient_permissions",
            "message": "Insufficient permissions",
            "expected_exception": "InsufficientPermissionsException",
        },
        {
            "status_code": 404,
            "error_type": "not_found",
            "message": "Resource not found",
            "expected_exception": "NotFoundException",
        },
        {
            "status_code": 429,
            "error_type": "rate_limit_exceeded",
            "message": "Rate limit exceeded",
            "expected_exception": "RateLimitExceededException",
        },
        {
            "status_code": 500,
            "error_type": "system",
            "message": "Internal server error",
            "expected_exception": "SystemException",
        },
    ]
    test_methods = [
        (nutrition_resource.get_food_log, {"date": "2025-02-08"}),
        (nutrition_resource.search_foods, {"query": "test"}),
        (
            nutrition_resource.create_food_log,
            {
                "date": "2025-02-08",
                "meal_type_id": MealType.BREAKFAST,
                "unit_id": 147,
                "amount": 100.0,
                "food_id": 12345,
            },
        ),
    ]
    for error_case in error_cases:
        error_response = mock_response_factory(
            error_case["status_code"],
            {"errors": [{"errorType": error_case["error_type"], "message": error_case["message"]}]},
        )
        nutrition_resource.oauth.request.return_value = error_response
        for method, params in test_methods:
            with raises(Exception) as exc_info:
                method(**params)
            assert error_case["expected_exception"] in str(exc_info.typename)
            assert error_case["message"] in str(exc_info.value)
