# tests/fitbit_client/resources/nutrition/test_create_food_log_custom_minimal.py

"""Tests for the create_food_log_custom_minimal endpoint."""

# Local imports

# Local imports
from fitbit_client.resources._constants import MealType


def test_create_food_log_custom_minimal(nutrition_resource, mock_response):
    """Test creating custom food log with minimal parameters (no brand or nutritional values)"""
    mock_response.json.return_value = {"foodLog": {"logId": 12345}}
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.create_food_log(
        date="2025-02-08",
        meal_type_id=MealType.BREAKFAST,
        unit_id=147,
        amount=100.0,
        food_name="Custom Food",
        calories=200,
        brand_name=None,
        nutritional_values=None,
    )
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/foods/log.json",
        data=None,
        json=None,
        params={
            "date": "2025-02-08",
            "mealTypeId": 1,
            "unitId": 147,
            "amount": 100.0,
            "foodName": "Custom Food",
            "calories": 200,
        },
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
