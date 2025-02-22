# tests/resources/nutrition/test_create_food_log.py

"""Tests for the create_food_log endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.resources.constants import MealType
from fitbit_client.resources.constants import NutritionalValue


def test_create_food_log_with_food_id_success(nutrition_resource, mock_response):
    """Test successful creation of a food log entry using food ID"""
    mock_response.json.return_value = {
        "foodLog": {"logId": 12345, "loggedFood": {"foodId": 67890, "amount": 1.0}}
    }
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.create_food_log(
        date="2025-02-08",
        meal_type_id=MealType.BREAKFAST,
        unit_id=147,
        amount=100.0,
        food_id=67890,
        favorite=True,
    )
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/foods/log.json",
        data=None,
        json=None,
        params={
            "date": "2025-02-08",
            "mealTypeId": 1,
            "unitId": 147,
            "amount": 100.0,
            "foodId": 67890,
            "favorite": "true",
        },
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_create_food_log_with_custom_food_success(nutrition_resource, mock_response):
    """Test successful creation of a food log entry using custom food details"""
    mock_response.json.return_value = {
        "foodLog": {"logId": 12345, "loggedFood": {"name": "Custom Food", "amount": 1.0}}
    }
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.create_food_log(
        date="2025-02-08",
        meal_type_id=MealType.LUNCH,
        unit_id=147,
        amount=100.0,
        food_name="Custom Food",
        calories=200,
        brand_name="Test Brand",
        nutritional_values={
            NutritionalValue.PROTEIN: 20.0,
            NutritionalValue.TOTAL_CARBOHYDRATE: 30.0,
        },
    )
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/foods/log.json",
        data=None,
        json=None,
        params={
            "date": "2025-02-08",
            "mealTypeId": 3,
            "unitId": 147,
            "amount": 100.0,
            "foodName": "Custom Food",
            "calories": 200,
            "brandName": "Test Brand",
            "protein": 20.0,
            "totalCarbohydrate": 30.0,
        },
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_create_food_log_with_favorite_flag(nutrition_resource, mock_response):
    """Test that creating a food log with favorite=True sets the flag correctly"""
    mock_response.json.return_value = {
        "foodLog": {"logId": 12345, "loggedFood": {"foodId": 67890, "amount": 1.0}}
    }
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.create_food_log(
        date="2025-02-08",
        meal_type_id=MealType.BREAKFAST,
        unit_id=147,
        amount=100.0,
        food_id=67890,
        favorite=True,
    )
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/foods/log.json",
        data=None,
        json=None,
        params={
            "date": "2025-02-08",
            "mealTypeId": 1,
            "unitId": 147,
            "amount": 100.0,
            "foodId": 67890,
            "favorite": "true",
        },
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
    nutrition_resource.oauth.request.reset_mock()
    result = nutrition_resource.create_food_log(
        date="2025-02-08",
        meal_type_id=MealType.BREAKFAST,
        unit_id=147,
        amount=100.0,
        food_id=67890,
        favorite=False,
    )
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/foods/log.json",
        data=None,
        json=None,
        params={
            "date": "2025-02-08",
            "mealTypeId": 1,
            "unitId": 147,
            "amount": 100.0,
            "foodId": 67890,
        },
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_create_food_log_with_brand_name_only(nutrition_resource, mock_response):
    """Test creating food log with only brand name (lines 172-174)"""
    mock_response.json.return_value = {"foodLog": {"logId": 12345}}
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.create_food_log(
        date="2025-02-08",
        meal_type_id=MealType.BREAKFAST,
        unit_id=147,
        amount=100.0,
        food_name="Custom Food",
        calories=200,
        brand_name="Test Brand",
    )
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/foods/log.json",
        data=None,
        json=None,
        params={
            "date": "2025-02-08",
            "mealTypeId": 1,
            "unitId": 147,
            "amount": 100.0,
            "foodName": "Custom Food",
            "calories": 200,
            "brandName": "Test Brand",
        },
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_create_food_log_validation_error(nutrition_resource):
    """Test that creating a food log without required parameters raises ValueError"""
    with raises(ValueError) as exc_info:
        nutrition_resource.create_food_log(
            date="2025-02-08", meal_type_id=MealType.BREAKFAST, unit_id=147, amount=100.0
        )
    assert "Must provide either food_id or (food_name and calories)" in str(exc_info.value)


def test_create_food_log_invalid_date(nutrition_resource):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException):
        nutrition_resource.create_food_log(
            date="invalid-date",
            meal_type_id=MealType.BREAKFAST,
            unit_id=147,
            amount=100.0,
            food_id=67890,
        )


def test_create_food_log_allows_today(nutrition_resource, mock_response):
    """Test that 'today' is accepted as a valid date"""
    mock_response.json.return_value = {"foodLog": {"logId": 12345}}
    mock_response.headers = {"content-type": "application/json"}
    nutrition_resource.oauth.request.return_value = mock_response
    nutrition_resource.create_food_log(
        date="today", meal_type_id=MealType.BREAKFAST, unit_id=147, amount=100.0, food_id=67890
    )
