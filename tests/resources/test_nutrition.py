# tests/resources/test_nutrition.py

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.resources.constants import FoodFormType
from fitbit_client.resources.constants import FoodPlanIntensity
from fitbit_client.resources.constants import MealType
from fitbit_client.resources.constants import NutritionalValue
from fitbit_client.resources.constants import WaterUnit
from fitbit_client.resources.nutrition import NutritionResource


class TestNutritionResource:
    @fixture
    def nutrition_resource(self, mock_oauth_session, mock_logger):
        """Fixture to provide a NutritionResource instance with standard settings"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            resource = NutritionResource(
                oauth_session=mock_oauth_session, locale="en_US", language="en_US"
            )
            return resource

    def test_add_favorite_foods_success(self, nutrition_resource, mock_response):
        """Test successful addition of a food to favorites"""
        food_id = 12345
        mock_response.json.return_value = {"success": True}
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.add_favorite_foods(food_id=food_id)

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "POST",
            f"https://api.fitbit.com/1/user/-/foods/log/favorite/{food_id}.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_create_food_success(self, nutrition_resource, mock_response):
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
        )  # grams

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

    def test_create_food_log_with_food_id_success(self, nutrition_resource, mock_response):
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
        )  # grams

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

    def test_create_food_log_with_custom_food_success(self, nutrition_resource, mock_response):
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
        )  # grams

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

    def test_create_food_log_with_favorite_flag(self, nutrition_resource, mock_response):
        """Test that creating a food log with favorite=True sets the flag correctly"""
        mock_response.json.return_value = {
            "foodLog": {"logId": 12345, "loggedFood": {"foodId": 67890, "amount": 1.0}}
        }
        nutrition_resource.oauth.request.return_value = mock_response

        # Test with favorite=True
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

        # Reset mock
        nutrition_resource.oauth.request.reset_mock()

        # Test with favorite=False (should not include favorite parameter)
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

    def test_create_food_log_validation_error(self, nutrition_resource):
        """Test that creating a food log without required parameters raises ValueError"""
        with raises(ValueError) as exc_info:
            nutrition_resource.create_food_log(
                date="2025-02-08", meal_type_id=MealType.BREAKFAST, unit_id=147, amount=100.0
            )
        assert "Must provide either food_id or (food_name and calories)" in str(exc_info.value)

    def test_create_food_log_invalid_date(self, nutrition_resource):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException):
            nutrition_resource.create_food_log(
                date="invalid-date",
                meal_type_id=MealType.BREAKFAST,
                unit_id=147,
                amount=100.0,
                food_id=67890,
            )

    def test_create_food_log_allows_today(self, nutrition_resource, mock_response):
        """Test that 'today' is accepted as a valid date"""
        mock_response.json.return_value = {"foodLog": {"logId": 12345}}
        mock_response.headers = {"content-type": "application/json"}
        nutrition_resource.oauth.request.return_value = mock_response

        # Should not raise an exception
        nutrition_resource.create_food_log(
            date="today", meal_type_id=MealType.BREAKFAST, unit_id=147, amount=100.0, food_id=67890
        )

    def test_create_food_goal_with_calories_success(self, nutrition_resource, mock_response):
        """Test successful creation of a food goal using calories"""
        mock_response.json.return_value = {"goals": {"calories": 2000}}
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.create_food_goal(calories=2000)

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1/user/-/foods/log/goal.json",
            data=None,
            json=None,
            params={"calories": 2000},
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_create_food_goal_with_intensity_success(self, nutrition_resource, mock_response):
        """Test successful creation of a food goal using intensity"""
        mock_response.json.return_value = {
            "foodPlan": {"intensity": "EASIER"},
            "goals": {"calories": 2200},
        }
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.create_food_goal(
            intensity=FoodPlanIntensity.EASIER, personalized=True
        )

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1/user/-/foods/log/goal.json",
            data=None,
            json=None,
            params={"intensity": "EASIER", "personalized": True},
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_create_food_goal_validation_error(self, nutrition_resource):
        """Test that creating a food goal without required parameters raises ValueError"""
        with raises(ValueError) as exc_info:
            nutrition_resource.create_food_goal()
        assert "Must provide either calories or intensity" in str(exc_info.value)

    def test_create_meal_success(self, nutrition_resource, mock_response):
        """Test successful creation of a meal"""
        mock_response.json.return_value = {
            "meal": {
                "id": 12345,
                "name": "Test Meal",
                "description": "Test meal description",
                "mealFoods": [{"foodId": 67890, "amount": 100.0, "unitId": 147}],
            }
        }
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

    def test_create_water_goal_success(self, nutrition_resource, mock_response):
        """Test successful creation of a water goal"""
        mock_response.json.return_value = {"goal": {"goal": 2000.0, "startDate": "2025-02-08"}}
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.create_water_goal(target=2000.0)

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1/user/-/foods/log/water/goal.json",
            data=None,
            json=None,
            params={"target": 2000.0},
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_create_water_log_success(self, nutrition_resource, mock_response):
        """Test successful creation of a water log entry"""
        mock_response.json.return_value = {"waterLog": {"logId": 12345, "amount": 500.0}}
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.create_water_log(
            amount=500.0, date="2025-02-08", unit=WaterUnit.MILLILITERS
        )

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1/user/-/foods/log/water.json",
            data=None,
            json=None,
            params={"amount": 500.0, "date": "2025-02-08", "unit": "ml"},
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_create_water_log_invalid_date(self, nutrition_resource):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException):
            nutrition_resource.create_water_log(amount=500.0, date="invalid-date")

    def test_create_water_log_allows_today(self, nutrition_resource, mock_response):
        """Test that 'today' is accepted as a valid date"""
        mock_response.json.return_value = {"waterLog": {"logId": 12345}}
        mock_response.headers = {"content-type": "application/json"}
        nutrition_resource.oauth.request.return_value = mock_response

        # Should not raise an exception
        nutrition_resource.create_water_log(amount=500.0, date="today")

    def test_delete_custom_food_success(self, nutrition_resource, mock_response):
        """Test successful deletion of a custom food"""
        mock_response.status_code = 204
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

    def test_delete_favorite_food_success(self, nutrition_resource, mock_response):
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

    def test_delete_food_log_success(self, nutrition_resource, mock_response):
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

    def test_delete_meal_success(self, nutrition_resource, mock_response):
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

    def test_delete_water_log_success(self, nutrition_resource, mock_response):
        """Test successful deletion of a water log entry"""
        mock_response.status_code = 204
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.delete_water_log(water_log_id=12345)

        assert result is None
        nutrition_resource.oauth.request.assert_called_once_with(
            "DELETE",
            "https://api.fitbit.com/1/user/-/foods/log/water/12345.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_food_success(self, nutrition_resource, mock_response):
        """Test successful retrieval of food details"""
        mock_response.json.return_value = {
            "food": {
                "foodId": 12345,
                "name": "Test Food",
                "calories": 100,
                "defaultServingSize": 100.0,
            }
        }
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.get_food(food_id=12345)

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/foods/12345.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_food_goals_success(self, nutrition_resource, mock_response):
        """Test successful retrieval of food goals"""
        mock_response.json.return_value = {
            "goals": {"calories": 2000},
            "foodPlan": {"intensity": "MAINTENANCE"},
        }
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.get_food_goals()

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/foods/log/goal.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_food_log_success(self, nutrition_resource, mock_response):
        """Test successful retrieval of food log entries"""
        mock_response.json.return_value = {
            "foods": [{"logId": 12345, "loggedFood": {"foodId": 67890, "amount": 100.0}}],
            "summary": {"calories": 500},
        }
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.get_food_log(date="2025-02-08")

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/foods/log/date/2025-02-08.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_food_log_invalid_date(self, nutrition_resource):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException):
            nutrition_resource.get_food_log("invalid-date")

    def test_get_food_log_allows_today(self, nutrition_resource, mock_response):
        """Test that 'today' is accepted as a valid date"""
        mock_response.json.return_value = {"foods": []}
        mock_response.headers = {"content-type": "application/json"}
        nutrition_resource.oauth.request.return_value = mock_response

        # Should not raise an exception
        nutrition_resource.get_food_log("today")

    def test_get_food_locales_success(self, nutrition_resource, mock_response):
        """Test successful retrieval of food locales"""
        mock_response.json.return_value = [
            {"value": "en_US", "label": "United States"},
            {"value": "en_GB", "label": "United Kingdom"},
        ]
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.get_food_locales()

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/foods/locales.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_food_units_success(self, nutrition_resource, mock_response):
        """Test successful retrieval of food units"""
        mock_response.json.return_value = [
            {"id": 147, "name": "gram", "plural": "grams"},
            {"id": 204, "name": "medium", "plural": "mediums"},
        ]
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.get_food_units()

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/foods/units.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_frequent_foods_success(self, nutrition_resource, mock_response):
        """Test successful retrieval of frequent foods"""
        mock_response.json.return_value = [
            {"foodId": 12345, "name": "Test Food", "amount": 100.0, "mealTypeId": 1}
        ]
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.get_frequent_foods()

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/foods/log/frequent.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_recent_foods_success(self, nutrition_resource, mock_response):
        """Test successful retrieval of recent foods"""
        mock_response.json.return_value = [
            {"foodId": 12345, "name": "Test Food", "amount": 100.0, "dateLastEaten": "2025-02-08"}
        ]
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.get_recent_foods()

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/foods/log/recent.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_favorite_foods_success(self, nutrition_resource, mock_response):
        """Test successful retrieval of favorite foods"""
        mock_response.json.return_value = [
            {"foodId": 12345, "name": "Test Food", "defaultServingSize": 100.0, "calories": 100}
        ]
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.get_favorite_foods()

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/foods/log/favorite.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_meal_success(self, nutrition_resource, mock_response):
        """Test successful retrieval of a meal"""
        mock_response.json.return_value = {
            "meal": {
                "id": 12345,
                "name": "Test Meal",
                "description": "Test meal description",
                "mealFoods": [{"foodId": 67890, "amount": 100.0, "unitId": 147}],
            }
        }
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

    def test_get_meals_success(self, nutrition_resource, mock_response):
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

    def test_get_water_goal_success(self, nutrition_resource, mock_response):
        """Test successful retrieval of water goal"""
        mock_response.json.return_value = {"goal": {"goal": 2000.0, "startDate": "2025-02-08"}}
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.get_water_goal()

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/foods/log/water/goal.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_water_log_success(self, nutrition_resource, mock_response):
        """Test successful retrieval of water log entries"""
        mock_response.json.return_value = {
            "water": [{"logId": 12345, "amount": 500.0}],
            "summary": {"water": 500.0},
        }
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.get_water_log(date="2025-02-08")

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/foods/log/water/date/2025-02-08.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_water_log_invalid_date(self, nutrition_resource):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException):
            nutrition_resource.get_water_log("invalid-date")

    def test_get_water_log_allows_today(self, nutrition_resource, mock_response):
        """Test that 'today' is accepted as a valid date"""
        mock_response.json.return_value = {"water": []}
        mock_response.headers = {"content-type": "application/json"}
        nutrition_resource.oauth.request.return_value = mock_response

        # Should not raise an exception
        nutrition_resource.get_water_log("today")

    def test_search_foods_success(self, nutrition_resource, mock_response):
        """Test successful food search"""
        mock_response.json.return_value = {
            "foods": [
                {"foodId": 12345, "name": "Test Food", "brand": "Test Brand", "calories": 100}
            ]
        }
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.search_foods(query="test food")

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/foods/search.json",
            data=None,
            json=None,
            params={"query": "test food"},
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_update_food_log_with_unit_amount_success(self, nutrition_resource, mock_response):
        """Test successful update of a food log entry with unit and amount"""
        mock_response.json.return_value = {
            "foodLog": {"logId": 12345, "loggedFood": {"foodId": 67890, "amount": 200.0}}
        }
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.update_food_log(
            food_log_id=12345, meal_type_id=MealType.LUNCH, unit_id=147, amount=200.0
        )

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1/user/-/foods/log/12345.json",
            data=None,
            json=None,
            params={"mealTypeId": 3, "unitId": 147, "amount": 200.0},
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_update_food_log_with_calories_success(self, nutrition_resource, mock_response):
        """Test successful update of a food log entry with calories"""
        mock_response.json.return_value = {
            "foodLog": {"logId": 12345, "loggedFood": {"calories": 300}}
        }
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.update_food_log(
            food_log_id=12345, meal_type_id=MealType.LUNCH, calories=300
        )

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1/user/-/foods/log/12345.json",
            data=None,
            json=None,
            params={"mealTypeId": 3, "calories": 300},
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_update_food_log_validation_error(self, nutrition_resource):
        """Test that updating a food log without required parameters raises ValueError"""
        with raises(ValueError) as exc_info:
            nutrition_resource.update_food_log(food_log_id=12345, meal_type_id=MealType.LUNCH)
        assert "Must provide either (unit_id and amount) or calories" in str(exc_info.value)

    def test_update_meal_success(self, nutrition_resource, mock_response):
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

    def test_update_water_log_success(self, nutrition_resource, mock_response):
        """Test successful update of a water log entry"""
        mock_response.json.return_value = {"waterLog": {"logId": 12345, "amount": 1000.0}}
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.update_water_log(
            water_log_id=12345, amount=1000.0, unit=WaterUnit.MILLILITERS
        )

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1/user/-/foods/log/water/12345.json",
            data=None,
            json=None,
            params={"amount": 1000.0, "unit": "ml"},
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_custom_user_id(self, nutrition_resource, mock_response):
        """Test that endpoints correctly handle custom user IDs"""
        custom_user_id = "123ABC"
        test_cases = [
            (
                nutrition_resource.get_food_log,
                {"date": "2025-02-08", "user_id": custom_user_id},
                f"https://api.fitbit.com/1/user/{custom_user_id}/foods/log/date/2025-02-08.json",
            ),
            (
                nutrition_resource.create_food_log,
                {
                    "date": "2025-02-08",
                    "meal_type_id": MealType.BREAKFAST,
                    "unit_id": 147,
                    "amount": 100.0,
                    "food_id": 12345,
                    "user_id": custom_user_id,
                },
                f"https://api.fitbit.com/1/user/{custom_user_id}/foods/log.json",
            ),
            (
                nutrition_resource.get_water_log,
                {"date": "2025-02-08", "user_id": custom_user_id},
                f"https://api.fitbit.com/1/user/{custom_user_id}/foods/log/water/date/2025-02-08.json",
            ),
        ]

        mock_response.json.return_value = {"success": True}
        nutrition_resource.oauth.request.return_value = mock_response

        for method, params, expected_url in test_cases:
            result = method(**params)
            assert result == mock_response.json.return_value
            last_call = nutrition_resource.oauth.request.call_args_list[-1]
            assert last_call[0][1] == expected_url

    def test_error_handling(self, nutrition_resource, mock_response_factory):
        """Test error handling for various error types and status codes"""
        error_cases = [
            {
                "status_code": 400,
                "error_type": "validation",
                "message": "Invalid parameters",
                "expected_exception": "ValidationException",
            },
            {
                "status_code": 401,
                "error_type": "invalid_token",
                "message": "Access token expired",
                "expected_exception": "InvalidTokenException",
            },
            {
                "status_code": 403,
                "error_type": "insufficient_permissions",
                "message": "Insufficient permissions",
                "expected_exception": "InsufficientPermissionsException",
            },
            {
                "status_code": 404,
                "error_type": "not_found",
                "message": "Resource not found",
                "expected_exception": "NotFoundException",
            },
            {
                "status_code": 429,
                "error_type": "rate_limit_exceeded",
                "message": "Rate limit exceeded",
                "expected_exception": "RateLimitExceededException",
            },
            {
                "status_code": 500,
                "error_type": "system",
                "message": "Internal server error",
                "expected_exception": "SystemException",
            },
        ]

        # Test methods
        test_methods = [
            (nutrition_resource.get_food_log, {"date": "2025-02-08"}),
            (nutrition_resource.search_foods, {"query": "test"}),
            (
                nutrition_resource.create_food_log,
                {
                    "date": "2025-02-08",
                    "meal_type_id": MealType.BREAKFAST,
                    "unit_id": 147,
                    "amount": 100.0,
                    "food_id": 12345,
                },
            ),
        ]

        for error_case in error_cases:
            error_response = mock_response_factory(
                error_case["status_code"],
                {
                    "errors": [
                        {"errorType": error_case["error_type"], "message": error_case["message"]}
                    ]
                },
            )
            nutrition_resource.oauth.request.return_value = error_response

            for method, params in test_methods:
                with raises(Exception) as exc_info:
                    method(**params)
                assert error_case["expected_exception"] in str(exc_info.typename)
                assert error_case["message"] in str(exc_info.value)

    def test_create_food_with_string_nutritional_values(self, nutrition_resource, mock_response):
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
        )  # String keys

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

    def test_create_food_log_with_brand_name_only(self, nutrition_resource, mock_response):
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
        )  # Only brand name, no nutritional values

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

    def test_create_food_goal_intensity_without_personalized(
        self, nutrition_resource, mock_response
    ):
        """Test creating food goal with intensity but without personalized flag (lines 217-220)"""
        mock_response.json.return_value = {"foodPlan": {"intensity": "EASIER"}}
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.create_food_goal(intensity=FoodPlanIntensity.EASIER)

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1/user/-/foods/log/goal.json",
            data=None,
            json=None,
            params={"intensity": "EASIER"},
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_update_water_log_without_unit(self, nutrition_resource, mock_response):
        """Test updating water log without specifying unit (lines 733-735)"""
        mock_response.json.return_value = {"waterLog": {"logId": 12345, "amount": 1000.0}}
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.update_water_log(water_log_id=12345, amount=1000.0)

        assert result == mock_response.json.return_value
        nutrition_resource.oauth.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1/user/-/foods/log/water/12345.json",
            data=None,
            json=None,
            params={"amount": 1000.0},
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_create_food_log_custom_minimal(self, nutrition_resource, mock_response):
        """Test creating custom food log with minimal parameters (no brand or nutritional values)"""
        mock_response.json.return_value = {"foodLog": {"logId": 12345}}
        nutrition_resource.oauth.request.return_value = mock_response

        result = nutrition_resource.create_food_log(
            date="2025-02-08",
            meal_type_id=MealType.BREAKFAST,
            unit_id=147,
            amount=100.0,
            food_name="Custom Food",
            calories=200,
            brand_name=None,
            nutritional_values=None,
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
            },
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )
