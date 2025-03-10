# tests/fitbit_client/resources/nutrition/test_get_water_goal.py

"""Tests for the get_water_goal endpoint."""


def test_get_water_goal_success(nutrition_resource, mock_response_factory):
    """Test successful retrieval of water goal"""
    mock_response = mock_response_factory(
        200, {"goal": {"goal": 2000.0, "startDate": "2025-02-08"}}
    )
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.get_water_goal()
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/foods/log/water/goal.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
