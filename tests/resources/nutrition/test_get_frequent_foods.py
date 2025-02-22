# tests/resources/nutrition/test_get_frequent_foods.py

"""Tests for the get_frequent_foods endpoint."""


def test_get_frequent_foods_success(nutrition_resource, mock_response):
    """Test successful retrieval of frequent foods"""
    mock_response.json.return_value = [
        {"foodId": 12345, "name": "Test Food", "amount": 100.0, "mealTypeId": 1}
    ]
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.get_frequent_foods()
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/foods/log/frequent.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
