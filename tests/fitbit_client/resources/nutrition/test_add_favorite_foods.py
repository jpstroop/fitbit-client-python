# tests/fitbit_client/resources/nutrition/test_add_favorite_foods.py

"""Tests for the add_favorite_foods endpoint."""


def test_add_favorite_foods_success(nutrition_resource, mock_response):
    """Test successful addition of a food to favorites"""
    food_id = 12345
    mock_response.json.return_value = {"success": True}
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.add_favorite_foods(food_id=food_id)
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        f"https://api.fitbit.com/1/user/-/foods/log/favorite/{food_id}.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
