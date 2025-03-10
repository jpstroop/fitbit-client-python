# tests/fitbit_client/resources/nutrition/test_delete_custom_food.py

"""Tests for the delete_custom_food endpoint."""


def test_delete_custom_food_success(nutrition_resource, mock_response_factory):
    """Test successful deletion of a custom food"""
    mock_response = mock_response_factory(204)
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.delete_custom_food(food_id=12345)
    assert result is None
    nutrition_resource.oauth.request.assert_called_once_with(
        "DELETE",
        "https://api.fitbit.com/1/user/-/foods/12345.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
