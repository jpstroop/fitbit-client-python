# tests/resources/nutrition/test_get_recent_foods.py

"""Tests for the get_recent_foods endpoint."""


def test_get_recent_foods_success(nutrition_resource, mock_response):
    """Test successful retrieval of recent foods"""
    mock_response.json.return_value = [
        {"foodId": 12345, "name": "Test Food", "amount": 100.0, "dateLastEaten": "2025-02-08"}
    ]
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.get_recent_foods()
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/foods/log/recent.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
