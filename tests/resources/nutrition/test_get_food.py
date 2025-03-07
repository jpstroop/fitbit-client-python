# tests/resources/nutrition/test_get_food.py

"""Tests for the get_food endpoint."""


def test_get_food_success(nutrition_resource, mock_response):
    """Test successful retrieval of food details"""
    mock_response.json.return_value = {
        "food": {"foodId": 12345, "name": "Test Food", "calories": 100, "defaultServingSize": 100.0}
    }
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.get_food(food_id=12345)
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/foods/12345.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
