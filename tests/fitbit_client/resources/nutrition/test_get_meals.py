# tests/fitbit_client/resources/nutrition/test_get_meals.py

"""Tests for the get_meals endpoint."""


def test_get_meals_success(nutrition_resource, mock_response):
    """Test successful retrieval of all meals"""
    mock_response.json.return_value = {
        "meals": [
            {
                "id": 12345,
                "name": "Test Meal",
                "description": "Test meal description",
                "mealFoods": [{"foodId": 67890, "amount": 100.0, "unitId": 147}],
            }
        ]
    }
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.get_meals()
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/meals.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
