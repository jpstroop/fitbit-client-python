# tests/resources/nutrition/test_delete_favorite_foods.py

"""Tests for the delete_favorite_foods endpoint."""


def test_delete_favorite_food_success(nutrition_resource, mock_response):
    """Test successful deletion of a favorite food"""
    mock_response.status_code = 204
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.delete_favorite_food(food_id=12345)
    assert result is None
    nutrition_resource.oauth.request.assert_called_once_with(
        "DELETE",
        "https://api.fitbit.com/1/user/-/foods/log/favorite/12345.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
