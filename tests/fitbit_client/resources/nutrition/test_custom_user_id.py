# tests/fitbit_client/resources/nutrition/test_custom_user_id.py

"""Tests for the custom_user_id endpoint."""

# Local imports

# Local imports
from fitbit_client.resources._constants import MealType


def test_custom_user_id(nutrition_resource, mock_response):
    """Test that endpoints correctly handle custom user IDs"""
    custom_user_id = "123ABC"
    test_cases = [
        (
            nutrition_resource.get_food_log,
            {"date": "2025-02-08", "user_id": custom_user_id},
            f"https://api.fitbit.com/1/user/{custom_user_id}/foods/log/date/2025-02-08.json",
        ),
        (
            nutrition_resource.create_food_log,
            {
                "date": "2025-02-08",
                "meal_type_id": MealType.BREAKFAST,
                "unit_id": 147,
                "amount": 100.0,
                "food_id": 12345,
                "user_id": custom_user_id,
            },
            f"https://api.fitbit.com/1/user/{custom_user_id}/foods/log.json",
        ),
        (
            nutrition_resource.get_water_log,
            {"date": "2025-02-08", "user_id": custom_user_id},
            f"https://api.fitbit.com/1/user/{custom_user_id}/foods/log/water/date/2025-02-08.json",
        ),
    ]
    mock_response.json.return_value = {"success": True}
    nutrition_resource.oauth.request.return_value = mock_response
    for method, params, expected_url in test_cases:
        result = method(**params)
        assert result == mock_response.json.return_value
        last_call = nutrition_resource.oauth.request.call_args_list[-1]
        assert last_call[0][1] == expected_url
