# resources/nutrition.py
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from resources.base import BaseResource
from resources.constants import FoodFormType
from resources.constants import FoodPlanIntensity
from resources.constants import MealType
from resources.constants import NutritionalValue
from resources.constants import WaterUnit


class NutritionResource(BaseResource):
    """
    Handles Fitbit Nutrition API endpoints for managing food logs, meals, and nutritional goals.

    API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/

    This resource provides functionality for:
    - Managing food and meal logs
    - Setting and retrieving nutritional goals
    - Managing favorite foods
    - Tracking water consumption

    Note:
        This resource requires the 'nutrition' scope.
        Food entries can be either PUBLIC (from Fitbit's database) or PRIVATE (user-created).
        When logging foods, prefer using food_id from Fitbit's database when possible.
    """

    def create_food(
        self,
        name: str,
        default_food_measurement_unit_id: int,
        default_serving_size: float,
        calories: int,
        description: str,
        form_type: FoodFormType,
        nutritional_values: Dict[NutritionalValue, float],
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Creates a new private food entry for a user.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/create-food/

        Args:
            name: Name of the food being created
            default_food_measurement_unit_id: ID from the food units endpoint
            default_serving_size: Size of default serving with nutritional values
            calories: Number of calories for default serving size
            description: Description of the food
            form_type: Food texture - either LIQUID or DRY
            nutritional_values: Dictionary mapping NutritionalValue constants to their amounts
            user_id: Optional user ID, defaults to current user

        Returns:
            Created food entry details including food ID and nutritional values
        """
        params = {
            "name": name,
            "defaultFoodMeasurementUnitId": default_food_measurement_unit_id,
            "defaultServingSize": default_serving_size,
            "calories": calories,
            "description": description,
            "formType": form_type.value,
            **{k.value: v for k, v in nutritional_values.items()},
        }
        return self._post("foods.json", params=params, user_id=user_id)

    def create_food_log(
        self,
        date: str,
        meal_type_id: MealType,
        unit_id: int,
        amount: float,
        food_id: Optional[int] = None,
        food_name: Optional[str] = None,
        favorite: bool = False,
        brand_name: Optional[str] = None,
        calories: Optional[int] = None,
        nutritional_values: Optional[Dict[NutritionalValue, float]] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Creates a food log entry for a given day.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/create-food-log/

        Args:
            date: Log date in yyyy-MM-dd format
            meal_type_id: Meal type (BREAKFAST, MORNING_SNACK, LUNCH, etc.)
            unit_id: Unit ID from food units endpoint
            amount: Amount consumed in specified unit (X.XX format)
            food_id: Optional ID of food from Fitbit's database
            food_name: Optional custom food name (required if food_id not provided)
            favorite: Optional flag to add food to favorites (only with food_id)
            brand_name: Optional brand name for custom foods
            calories: Optional calories for custom foods
            nutritional_values: Optional dictionary mapping NutritionalValue constants to their amounts
                            (only used with custom foods)
            user_id: Optional user ID, defaults to current user

        Returns:
            Created food log entry details and daily summary

        Note:
            Either food_id or (food_name and calories) must be provided.
            Using food_id is recommended when possible.
            Nutritional values are only used when creating custom food logs.
        """
        if not food_id and not (food_name and calories):
            raise ValueError("Must provide either food_id or (food_name and calories)")

        params = {"date": date, "mealTypeId": meal_type_id.value, "unitId": unit_id, "amount": amount}

        if food_id:
            params["foodId"] = food_id
            if favorite:
                params["favorite"] = True
        else:
            params["foodName"] = food_name
            params["calories"] = calories
            if brand_name:
                params["brandName"] = brand_name
            if nutritional_values:
                params.update({k.value: v for k, v in nutritional_values.items()})

        return self._post("foods/log.json", params=params, user_id=user_id)

    def create_food_goal(
        self,
        calories: Optional[int] = None,
        intensity: Optional[FoodPlanIntensity] = None,
        personalized: Optional[bool] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Creates or updates a user's daily calorie consumption goal or food plan.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/create-food-goal/

        Args:
            calories: Optional manual calorie consumption goal
            intensity: Optional food plan intensity (MAINTENANCE, EASIER, MEDIUM,
                      KINDAHARD, HARDER)
            personalized: Optional food plan type (true/false)
            user_id: Optional user ID, defaults to current user

        Returns:
            Updated food goal information

        Note:
            Either calories or intensity must be provided.
            Food plan requires an active weight goal.
        """
        if not calories and not intensity:
            raise ValueError("Must provide either calories or intensity")

        params = {}
        if calories:
            params["calories"] = calories
        if intensity:
            params["intensity"] = intensity.value
            if personalized is not None:
                params["personalized"] = personalized

        return self._post("foods/log/goal.json", params=params, user_id=user_id)

    def create_meal(
        self, name: str, description: str, food_id: int, unit_id: int, amount: float, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Creates a meal with the given foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/create-meal/

        Args:
            name: Name of the meal
            description: Short description of the meal
            food_id: ID of food to include in meal
            unit_id: ID of units used
            amount: Amount consumed (X.XX format)
            user_id: Optional user ID, defaults to current user

        Returns:
            Created meal details including meal ID and food information

        Note:
            Meals are always associated with meal type "Anytime" (7).
        """
        data = {
            "name": name,
            "description": description,
            "mealFoods": [{"foodId": food_id, "amount": amount, "unitId": unit_id}],
        }
        return self._post("meals.json", json=data, user_id=user_id)

    def create_water_goal(self, target: float, user_id: str = "-") -> Dict[str, Any]:
        """
        Creates or updates a user's daily water consumption goal.

        API Reference:

        Args:
            target: Target water goal in the unit system matching locale
            user_id: Optional user ID, defaults to current user

        Returns:
            Updated water goal information
        """
        return self._post("foods/log/water/goal.json", params={"target": target}, user_id=user_id)

    def create_water_log(
        self, amount: float, date: str, unit: Optional[WaterUnit] = None, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Creates a water log entry.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/create-water-goal/

        Args:
            amount: Amount of water consumed (X.X format)
            date: Log date in yyyy-MM-dd format
            unit: Optional unit ('ml', 'fl oz', 'cup')
            user_id: Optional user ID, defaults to current user

        Returns:
            Created water log entry details

        Note:
            If unit is not specified, uses unit system from Accept-Language header.
        """
        params = {"amount": amount, "date": date}
        if unit:
            params["unit"] = unit.value
        return self._post("foods/log/water.json", params=params, user_id=user_id)

    def delete_custom_food(self, food_id: str, user_id: str = "-") -> None:
        """
        Deletes a custom food created by the user.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/delete-custom-food/

        Args:
            food_id: ID of the food to delete
            user_id: Optional user ID, defaults to current user
        """
        self._delete(f"foods/{food_id}.json", user_id=user_id)

    def delete_favorite_food(self, food_id: str, user_id: str = "-") -> None:
        """
        Removes a food from user's list of favorite foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/delete-favorite-foods/

        Args:
            food_id: ID of the food to remove from favorites
            user_id: Optional user ID, defaults to current user
        """
        self._delete(f"foods/log/favorite/{food_id}.json", user_id=user_id)

    def delete_food_log(self, food_log_id: str, user_id: str = "-") -> None:
        """
        Deletes a food log entry.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/delete-food-log/

        Args:
            food_log_id: ID of the food log to delete
            user_id: Optional user ID, defaults to current user
        """
        self._delete(f"foods/log/{food_log_id}.json", user_id=user_id)

    def delete_meal(self, meal_id: str, user_id: str = "-") -> None:
        """
        Deletes a meal.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/delete-meal/

        Args:
            meal_id: ID of the meal to delete
            user_id: Optional user ID, defaults to current user
        """
        self._delete(f"meals/{meal_id}.json", user_id=user_id)

    def delete_water_log(self, water_log_id: str, user_id: str = "-") -> None:
        """
        Deletes a water log entry.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/delete-water-log/

        Args:
            water_log_id: ID of the water log to delete
            user_id: Optional user ID, defaults to current user
        """
        self._delete(f"foods/log/water/{water_log_id}.json", user_id=user_id)

    def get_food(self, food_id: str) -> Dict[str, Any]:
        """
        Retrieves details of a specific food from Fitbit's database or user's private foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-food/

        Args:
            food_id: ID of the food to retrieve

        Returns:
            Food details including nutritional information and available units

        Note:
            Nutritional values are only included for PRIVATE foods.
        """
        return self._get(f"foods/{food_id}.json", requires_user_id=False)

    def get_food_goals(self, user_id: str = "-") -> Dict[str, Any]:
        """
        Retrieves the user's daily calorie consumption goal and/or food plan.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-food-goals/

        Args:
            user_id: Optional user ID, defaults to current user

        Returns:
            Dict containing calorie goal and food plan if enabled

        Note:
            Food plan data is only included if the feature is enabled.
        """
        return self._get("foods/log/goal.json", user_id=user_id)

    def get_food_log(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Retrieves a summary of all food log entries for a given day.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-food-log/

        Args:
            date: The date in yyyy-MM-dd format or 'today'
            user_id: Optional user ID, defaults to current user

        Returns:
            Dictionary containing food log entries and daily summary
        """
        return self._get(f"foods/log/date/{date}.json", user_id=user_id)

    def get_food_locales(self) -> List[Dict[str, Any]]:
        """
        Retrieves the list of food locales used for searching and creating foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-food-log/

        Returns:
            List of supported locales with regional settings
        """
        return self._get("foods/locales.json", requires_user_id=False)

    def get_food_units(self) -> List[Dict[str, Any]]:
        """
        Retrieves list of valid Fitbit food units.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-food-units/

        Returns:
            List of available measurement units for food logging
        """
        return self._get("foods/units.json", requires_user_id=False)

    def get_frequent_foods(self, user_id: str = "-") -> List[Dict[str, Any]]:
        """
        Retrieves a list of user's frequently consumed foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-frequent-foods/

        Args:
            user_id: Optional user ID, defaults to current user

        Returns:
            List of frequently logged foods with serving information

        Note:
            Foods in the response can be quickly logged using create_food_log.
        """
        return self._get("foods/log/frequent.json", user_id=user_id)

    def get_recent_foods(self, user_id: str = "-") -> List[Dict[str, Any]]:
        """
        Retrieves a list of user's recently consumed foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-recent-foods/

        Args:
            user_id: Optional user ID, defaults to current user

        Returns:
            List of recently logged foods with dates and details
        """
        return self._get("foods/log/recent.json", user_id=user_id)

    def get_favorite_foods(self, user_id: str = "-") -> List[Dict[str, Any]]:
        """
        Retrieves a list of user's favorite foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-favorite-foods/

        Args:
            user_id: Optional user ID, defaults to current user

        Returns:
            List of foods marked as favorites
        """
        return self._get("foods/log/favorite.json", user_id=user_id)

    def get_meal(self, meal_id: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Retrieves a single meal from user's food log.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-meal/

        Args:
            meal_id: ID of the meal to retrieve
            user_id: Optional user ID, defaults to current user

        Returns:
            Meal details including constituent foods and nutritional info

        Note:
            All meals are associated with meal type "Anytime" (7).
        """
        return self._get(f"meals/{meal_id}.json", user_id=user_id)

    def get_meals(self, user_id: str = "-") -> Dict[str, Any]:
        """
        Retrieves list of all user's saved meals.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-meals/

        Args:
            user_id: Optional user ID, defaults to current user

        Returns:
            List of saved meals with their foods and nutritional info
        """
        return self._get("meals.json", user_id=user_id)

    def get_water_goal(self, user_id: str = "-") -> Dict[str, Any]:
        """
        Retrieves user's daily water consumption goal.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-water-goal/

        Args:
            user_id: Optional user ID, defaults to current user

        Returns:
            Water goal amount and start date
        """
        return self._get("foods/log/water/goal.json", user_id=user_id)

    def get_water_log(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Retrieves water log entries for a specific date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-water-log/

        Args:
            date: Log date in yyyy-MM-dd format
            user_id: Optional user ID, defaults to current user

        Returns:
            Water consumption summary and individual log entries
        """
        return self._get(f"foods/log/water/date/{date}.json", user_id=user_id)

    def search_foods(self, query: str) -> List[Dict[str, Any]]:
        """
        Searches Fitbit's food database and user's custom foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/search-foods/

        Args:
            query: Search string to match against food names

        Returns:
            List of matching foods with nutritional information

        Note:
            Results include both PUBLIC (Fitbit database) and PRIVATE (user-created) foods.
            Search uses the locale specified in accept-language header.
        """
        return self._get("foods/search.json", params={"query": query}, requires_user_id=False)

    def update_food_log(
        self,
        food_log_id: str,
        meal_type_id: MealType,
        unit_id: Optional[int] = None,
        amount: Optional[float] = None,
        calories: Optional[int] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Updates an existing food log entry.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/update-food-log/

        Args:
            food_log_id: ID of the food log to update
            meal_type_id: 1=Breakfast, 2=Morning Snack, 3=Lunch, 4=Afternoon Snack,
                         5=Dinner, 7=Anytime
            unit_id: Optional unit ID (required for foods with foodId)
            amount: Optional amount in specified unit (required for foods with foodId)
            calories: Optional calories (only for custom food logs)
            user_id: Optional user ID, defaults to current user

        Returns:
            Updated food log entry

        Note:
            Either (unit_id and amount) or calories must be provided.
            Only food logs with valid foodId can be updated with unit/amount.
        """
        params = {"mealTypeId": meal_type_id.value}
        if unit_id and amount:
            params.update({"unitId": unit_id, "amount": amount})
        elif calories:
            params["calories"] = calories
        else:
            raise ValueError("Must provide either (unit_id and amount) or calories")

        return self._post(f"foods/log/{food_log_id}.json", params=params, user_id=user_id)

    def update_meal(
        self, meal_id: str, name: str, description: str, foods: List[Dict[str, Any]], user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Updates an existing meal.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/update-meal/

        Args:
            meal_id: ID of the meal to update
            name: New name for the meal
            description: New description for the meal
            foods: List of foods with format:
                  [{"foodId": id, "amount": amount, "unitId": unit_id}, ...]
            user_id: Optional user ID, defaults to current user

        Returns:
            Updated meal information
        """
        data = {"name": name, "description": description, "mealFoods": foods}
        return self._post(f"meals/{meal_id}.json", json=data, user_id=user_id)

    def update_water_log(
        self, water_log_id: str, amount: float, unit: Optional[WaterUnit] = None, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Updates an existing water log entry.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/update-water-log/

        Args:
            water_log_id: ID of the water log to update
            amount: New amount consumed (X.X format)
            unit: Optional unit ('ml', 'fl oz', 'cup')
            user_id: Optional user ID, defaults to current user

        Returns:
            Updated water log entry

        Note:
            If unit is not specified, uses unit system from Accept-Language header.
        """
        params = {"amount": amount}
        if unit:
            params["unit"] = unit.value
        return self._post(f"foods/log/water/{water_log_id}.json", params=params, user_id=user_id)
