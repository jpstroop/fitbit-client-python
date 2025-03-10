# tests/fitbit_client/resources/nutrition/test_create_water_goal.py

"""Tests for the create_water_goal endpoint."""


def test_create_water_goal_success(nutrition_resource, mock_response):
    """Test successful creation of a water goal"""
    mock_response.json.return_value = {"goal": {"goal": 2000.0, "startDate": "2025-02-08"}}
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.create_water_goal(target=2000.0)
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/foods/log/water/goal.json",
        data=None,
        json=None,
        params={"target": 2000.0},
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
