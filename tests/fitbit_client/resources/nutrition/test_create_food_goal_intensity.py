# tests/fitbit_client/resources/nutrition/test_create_food_goal_intensity.py

"""Tests for the create_food_goal_intensity endpoint."""

# Local imports
from fitbit_client.resources._constants import FoodPlanIntensity


def test_create_food_goal_intensity_without_personalized(nutrition_resource, mock_response_factory):
    """Test creating food goal with intensity but without personalized flag (lines 217-220)"""
    mock_response = mock_response_factory(200, {"foodPlan": {"intensity": "EASIER"}})
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.create_food_goal(intensity=FoodPlanIntensity.EASIER)
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/foods/log/goal.json",
        data=None,
        json=None,
        params={"intensity": "EASIER"},
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
