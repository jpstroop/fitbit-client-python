# tests/fitbit_client/resources/nutrition/test_update_meal.py

"""Tests for the update_meal endpoint."""


def test_update_meal_success(nutrition_resource, mock_response):
    """Test successful update of a meal"""
    mock_response.json.return_value = {
        "meal": {
            "id": 12345,
            "name": "Updated Meal",
            "description": "Updated description",
            "mealFoods": [{"foodId": 67890, "amount": 200.0, "unitId": 147}],
        }
    }
    nutrition_resource.oauth.request.return_value = mock_response
    foods = [{"food_id": 67890, "amount": 200.0, "unit_id": 147}]
    result = nutrition_resource.update_meal(
        meal_id=12345, name="Updated Meal", description="Updated description", foods=foods
    )
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/meals/12345.json",
        data=None,
        json={
            "name": "Updated Meal",
            "description": "Updated description",
            "mealFoods": [{"foodId": 67890, "amount": 200.0, "unitId": 147}],
        },
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
