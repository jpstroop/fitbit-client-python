# tests/fitbit_client/resources/nutrition/test_create_food_goal.py

"""Tests for the create_food_goal endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import MissingParameterException
from fitbit_client.resources._constants import FoodPlanIntensity


def test_create_food_goal_with_calories_success(nutrition_resource, mock_response):
    """Test successful creation of a food goal using calories"""
    mock_response.json.return_value = {"goals": {"calories": 2000}}
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.create_food_goal(calories=2000)
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/foods/log/goal.json",
        data=None,
        json=None,
        params={"calories": 2000},
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_create_food_goal_with_intensity_success(nutrition_resource, mock_response):
    """Test successful creation of a food goal using intensity"""
    mock_response.json.return_value = {
        "foodPlan": {"intensity": "EASIER"},
        "goals": {"calories": 2200},
    }
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.create_food_goal(
        intensity=FoodPlanIntensity.EASIER, personalized=True
    )
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/foods/log/goal.json",
        data=None,
        json=None,
        params={"intensity": "EASIER", "personalized": True},
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_create_food_goal_validation_error(nutrition_resource):
    """Test that creating a food goal without required parameters raises MissingParameterException"""
    with raises(MissingParameterException) as exc_info:
        nutrition_resource.create_food_goal()
    assert "Must provide either calories or intensity" in str(exc_info.value)
    assert exc_info.value.field_name == "calories/intensity"
