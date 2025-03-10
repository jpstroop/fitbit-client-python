# tests/fitbit_client/resources/nutrition/test_update_food_log.py

"""Tests for the update_food_log endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import MissingParameterException
from fitbit_client.resources.constants import MealType


def test_update_food_log_with_unit_amount_success(nutrition_resource, mock_response):
    """Test successful update of a food log entry with unit and amount"""
    mock_response.json.return_value = {
        "foodLog": {"logId": 12345, "loggedFood": {"foodId": 67890, "amount": 200.0}}
    }
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.update_food_log(
        food_log_id=12345, meal_type_id=MealType.LUNCH, unit_id=147, amount=200.0
    )
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/foods/log/12345.json",
        data=None,
        json=None,
        params={"mealTypeId": 3, "unitId": 147, "amount": 200.0},
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_update_food_log_with_calories_success(nutrition_resource, mock_response):
    """Test successful update of a food log entry with calories"""
    mock_response.json.return_value = {"foodLog": {"logId": 12345, "loggedFood": {"calories": 300}}}
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.update_food_log(
        food_log_id=12345, meal_type_id=MealType.LUNCH, calories=300
    )
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/foods/log/12345.json",
        data=None,
        json=None,
        params={"mealTypeId": 3, "calories": 300},
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_update_food_log_validation_error(nutrition_resource):
    """Test that updating a food log without required parameters raises MissingParameterException"""
    with raises(MissingParameterException) as exc_info:
        nutrition_resource.update_food_log(food_log_id=12345, meal_type_id=MealType.LUNCH)
    assert "Must provide either (unit_id and amount) or calories" in str(exc_info.value)
    assert exc_info.value.field_name == "unit_id/amount/calories"
