# tests/resources/nutrition/test_get_food_goals.py

"""Tests for the get_food_goals endpoint."""


def test_get_food_goals_success(nutrition_resource, mock_response):
    """Test successful retrieval of food goals"""
    mock_response.json.return_value = {
        "goals": {"calories": 2000},
        "foodPlan": {"intensity": "MAINTENANCE"},
    }
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.get_food_goals()
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/foods/log/goal.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
