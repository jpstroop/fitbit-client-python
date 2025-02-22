# tests/resources/nutrition/test_get_favorite_foods.py

"""Tests for the get_favorite_foods endpoint."""


def test_get_favorite_foods_success(nutrition_resource, mock_response):
    """Test successful retrieval of favorite foods"""
    mock_response.json.return_value = [
        {"foodId": 12345, "name": "Test Food", "defaultServingSize": 100.0, "calories": 100}
    ]
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.get_favorite_foods()
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/foods/log/favorite.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
