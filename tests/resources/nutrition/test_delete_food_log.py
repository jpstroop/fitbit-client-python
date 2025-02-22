# tests/resources/nutrition/test_delete_food_log.py

"""Tests for the delete_food_log endpoint."""


def test_delete_food_log_success(nutrition_resource, mock_response):
    """Test successful deletion of a food log entry"""
    mock_response.status_code = 204
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.delete_food_log(food_log_id=12345)
    assert result is None
    nutrition_resource.oauth.request.assert_called_once_with(
        "DELETE",
        "https://api.fitbit.com/1/user/-/foods/log/12345.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
