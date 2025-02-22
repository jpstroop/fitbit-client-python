# tests/resources/nutrition/test_create_food.py

"""Tests for the create_food endpoint."""

# Local imports

# Local imports
from fitbit_client.resources.constants import FoodFormType
from fitbit_client.resources.constants import NutritionalValue


def test_create_food_success(nutrition_resource, mock_response):
    """Test successful creation of a new food"""
    mock_response.json.return_value = {"foodId": 12345, "name": "Test Food", "calories": 100}
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.create_food(
        name="Test Food",
        default_food_measurement_unit_id=147,
        default_serving_size=100.0,
        calories=100,
        description="Test food description",
        form_type=FoodFormType.DRY,
        nutritional_values={
            NutritionalValue.PROTEIN: 20.0,
            NutritionalValue.TOTAL_CARBOHYDRATE: 0.0,
        },
    )
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/foods.json",
        data=None,
        json=None,
        params={
            "name": "Test Food",
            "defaultFoodMeasurementUnitId": 147,
            "defaultServingSize": 100.0,
            "calories": 100,
            "description": "Test food description",
            "formType": "DRY",
            "protein": 20.0,
            "totalCarbohydrate": 0.0,
        },
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_create_food_with_string_nutritional_values(nutrition_resource, mock_response):
    """Test creating food with string nutritional value keys (line 94)"""
    mock_response.json.return_value = {"foodId": 12345, "name": "Test Food"}
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.create_food(
        name="Test Food",
        default_food_measurement_unit_id=147,
        default_serving_size=100.0,
        calories=100,
        description="Test description",
        form_type=FoodFormType.DRY,
        nutritional_values={"protein": 20.0, "totalCarbohydrate": 30.0},
    )
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/foods.json",
        data=None,
        json=None,
        params={
            "name": "Test Food",
            "defaultFoodMeasurementUnitId": 147,
            "defaultServingSize": 100.0,
            "calories": 100,
            "description": "Test description",
            "formType": "DRY",
            "protein": 20.0,
            "totalCarbohydrate": 30.0,
        },
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
