# tests/fitbit_client/resources/nutrition/test_get_meal.py

"""Tests for the get_meal endpoint."""


def test_get_meal_success(nutrition_resource, mock_response_factory):
    """Test successful retrieval of a meal"""
    mock_response = mock_response_factory(
        200,
        {
            "meal": {
                "id": 12345,
                "name": "Test Meal",
                "description": "Test meal description",
                "mealFoods": [{"foodId": 67890, "amount": 100.0, "unitId": 147}],
            }
        },
    )
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.get_meal(meal_id=12345)
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/meals/12345.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
