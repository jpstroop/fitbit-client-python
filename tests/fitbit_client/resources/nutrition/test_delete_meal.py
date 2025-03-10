# tests/fitbit_client/resources/nutrition/test_delete_meal.py

"""Tests for the delete_meal endpoint."""


def test_delete_meal_success(nutrition_resource, mock_response):
    """Test successful deletion of a meal"""
    mock_response.status_code = 204
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.delete_meal(meal_id=12345)
    assert result is None
    nutrition_resource.oauth.request.assert_called_once_with(
        "DELETE",
        "https://api.fitbit.com/1/user/-/meals/12345.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
