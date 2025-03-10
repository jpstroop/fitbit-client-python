# tests/fitbit_client/resources/nutrition/test_create_meal.py

"""Tests for the create_meal endpoint."""


def test_create_meal_success(nutrition_resource, mock_response_factory):
    """Test successful creation of a meal"""
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
    foods = [{"food_id": 67890, "amount": 100.0, "unit_id": 147}]
    result = nutrition_resource.create_meal(
        name="Test Meal", description="Test meal description", foods=foods
    )
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/meals.json",
        data=None,
        json={
            "name": "Test Meal",
            "description": "Test meal description",
            "mealFoods": [{"foodId": 67890, "amount": 100.0, "unitId": 147}],
        },
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
