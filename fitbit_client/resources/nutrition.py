# fitbit_client/resources/nutrition.py

# Standard library imports
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from typing import cast

# Local imports
from fitbit_client.exceptions import ClientValidationException
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import FoodFormType
from fitbit_client.resources.constants import FoodPlanIntensity
from fitbit_client.resources.constants import MealType
from fitbit_client.resources.constants import NutritionalValue
from fitbit_client.resources.constants import WaterUnit
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.helpers import to_camel_case
from fitbit_client.utils.types import JSONDict
from fitbit_client.utils.types import JSONList
from fitbit_client.utils.types import ParamDict


class NutritionResource(BaseResource):
    """
    Handles Fitbit Nutrition API endpoints for managing food logs, meals, and nutritional goals.

    API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/
    """

    def add_favorite_foods(self, food_id: int, user_id: str = "-", debug: bool = False) -> None:
        """
        Adds a food with the given ID to the user's list of favorite foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/add-favorite-foods/

        Args:
            food_id: ID of the food to add to favorites
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Response indicating success
        """
        result = self._make_request(
            f"foods/log/favorite/{food_id}.json", user_id=user_id, http_method="POST", debug=debug
        )
        return cast(None, result)

    # Semantically correct aliases for above.
    add_favorite_food = add_favorite_foods  # Arguable
    create_favorite_food = add_favorite_foods  # Better

    def create_food(
        self,
        name: str,
        default_food_measurement_unit_id: int,
        default_serving_size: float,
        calories: int,
        description: str,
        form_type: FoodFormType,
        nutritional_values: Dict[NutritionalValue | str, float | int],
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
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
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Created food entry details including food ID and nutritional values
        """
        params: ParamDict = {
            "name": name,
            "defaultFoodMeasurementUnitId": default_food_measurement_unit_id,
            "defaultServingSize": default_serving_size,
            "calories": calories,
            "description": description,
            "formType": str(form_type.value),
        }

        if (
            nutritional_values
            and NutritionalValue.CALORIES_FROM_FAT in nutritional_values
            and not isinstance(nutritional_values[NutritionalValue.CALORIES_FROM_FAT], int)
        ):
            raise ClientValidationException(
                message="Calories from fat must be an integer",
                error_type="client_validation",
                field_name="CALORIES_FROM_FAT",
            )
        for key, value in nutritional_values.items():
            if isinstance(key, NutritionalValue):
                if key == NutritionalValue.CALORIES_FROM_FAT:
                    params[key.value] = int(value)
                else:
                    params[key.value] = float(value)
            else:
                params[str(key)] = float(value)

        result = self._make_request(
            "foods.json", params=params, user_id=user_id, http_method="POST", debug=debug
        )
        return cast(JSONDict, result)

    @validate_date_param(field_name="date")
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
        nutritional_values: Optional[Dict[NutritionalValue, float | int]] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
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
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Created food log entry details and daily summary

        Raises:
            ValueError: Must provide either food_id or (food_name and calories)
            InvalidDateException: If date format is invalid

        Note:
            Either food_id or (food_name and calories) must be provided.
            Using food_id is recommended when possible.
            Nutritional values are only used when creating custom food logs.
            unit_id must match one of the units associated with the food. It may
                also be that it can only match the default_food_measurement_unit_id
                for a food you created.
        """
        if not food_id and not (food_name and calories):
            raise ClientValidationException(
                "Must provide either food_id or (food_name and calories)"
            )

        params: ParamDict = {
            "date": date,
            "mealTypeId": int(meal_type_id.value),
            "unitId": unit_id,
            "amount": amount,
        }

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
                # Convert enum keys to strings and ensure values are floats
                for k, v in nutritional_values.items():
                    key_str = k.value if isinstance(k, NutritionalValue) else str(k)
                    params[key_str] = float(v)

        result = self._make_request(
            "foods/log.json", params=params, user_id=user_id, http_method="POST", debug=debug
        )
        return cast(JSONDict, result)

    def create_food_goal(
        self,
        calories: Optional[int] = None,
        intensity: Optional[FoodPlanIntensity] = None,
        personalized: Optional[bool] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """
        Creates or updates a user's daily calorie consumption goal or food plan.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/create-food-goal/

        Args:
            calories: Optional manual calorie consumption goal
            intensity: Optional food plan intensity (MAINTENANCE, EASIER, MEDIUM,
                      KINDAHARD, HARDER)
            personalized: Optional food plan type (true/false)
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Updated food goal information

        Note:
            Either calories or intensity must be provided.
            Food plan requires an active weight goal.
        """
        if not calories and not intensity:
            raise ValueError("Must provide either calories or intensity")

        params: ParamDict = {}
        if calories:
            params["calories"] = calories
        if intensity:
            params["intensity"] = str(intensity.value)
            if personalized is not None:
                params["personalized"] = personalized

        result = self._make_request(
            "foods/log/goal.json", params=params, user_id=user_id, http_method="POST", debug=debug
        )
        return cast(JSONDict, result)

    def create_meal(
        self,
        name: str,
        description: str,
        foods: List[JSONDict],
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """
        Creates a meal with the given foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/create-meal/

        Args:
            name: Name of the meal
            description: Short description of the meal
            foods: A list of dicts with the following entries (all required):
                food_id: ID of food to include in meal
                unit_id: ID of units used
                amount: Amount consumed (X.XX format)
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Created meal details including meal ID and food information

        Note:
            Meals are always associated with meal type "Anytime" (7).
        """
        # snakes to camels
        foods = [{to_camel_case(k): v for k, v in d.items()} for d in foods]
        data = {"name": name, "description": description, "mealFoods": foods}
        result = self._make_request(
            "meals.json", json=data, user_id=user_id, http_method="POST", debug=debug
        )
        return cast(JSONDict, result)

    def create_water_goal(self, target: float, user_id: str = "-", debug: bool = False) -> JSONDict:
        """
        Creates or updates a user's daily water consumption goal.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/create-water-goal/

        Args:
            target: Target water goal in the unit system matching locale
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Updated water goal information
        """
        result = self._make_request(
            "foods/log/water/goal.json",
            params={"target": target},
            user_id=user_id,
            http_method="POST",
            debug=debug,
        )
        return cast(JSONDict, result)

    @validate_date_param(field_name="date")
    def create_water_log(
        self,
        amount: float,
        date: str,
        unit: Optional[WaterUnit] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """
        Creates a water log entry.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/create-water-log/

        Args:
            amount: Amount of water consumed (X.X format)
            date: Log date in yyyy-MM-dd format
            unit: Optional unit ('ml', 'fl oz', 'cup')
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Created water log entry details

        Raises:
            InvalidDateException: If date format is invalid

        Note:
            If unit is not specified, uses unit system from Accept-Language
            header. This can be specified when the client is initialized.
        """
        params: ParamDict = {"amount": amount, "date": date}
        if unit:
            params["unit"] = str(unit.value)
        result = self._make_request(
            "foods/log/water.json", params=params, user_id=user_id, http_method="POST", debug=debug
        )
        return cast(JSONDict, result)

    def delete_custom_food(self, food_id: int, user_id: str = "-", debug: bool = False) -> None:
        """
        Deletes a custom food created by the user.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/delete-custom-food/

        Args:
            food_id: ID of the food to delete
            user_id: Optional user ID, defaults to current user
        """
        result = self._make_request(
            f"foods/{food_id}.json", user_id=user_id, http_method="DELETE", debug=debug
        )
        return cast(None, result)

    def delete_favorite_foods(self, food_id: int, user_id: str = "-", debug: bool = False) -> None:
        """
        Removes a food from user's list of favorite foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/delete-favorite-foods/

        Args:
            food_id: ID of the food to remove from favorites
            user_id: Optional user ID, defaults to current user
        """
        result = self._make_request(
            f"foods/log/favorite/{food_id}.json", user_id=user_id, http_method="DELETE", debug=debug
        )
        return cast(None, result)

    delete_favorite_food = delete_favorite_foods  # semantically correct alias

    def delete_food_log(self, food_log_id: int, user_id: str = "-", debug: bool = False) -> None:
        """
        Deletes a food log entry.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/delete-food-log/

        Args:
            food_log_id: ID of the food log to delete
            user_id: Optional user ID, defaults to current user
        """
        result = self._make_request(
            f"foods/log/{food_log_id}.json", user_id=user_id, http_method="DELETE", debug=debug
        )
        return cast(None, result)

    def delete_meal(self, meal_id: int, user_id: str = "-", debug: bool = False) -> None:
        """
        Deletes a meal.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/delete-meal/

        Args:
            meal_id: ID of the meal to delete
            user_id: Optional user ID, defaults to current user
        """
        result = self._make_request(
            f"meals/{meal_id}.json", user_id=user_id, http_method="DELETE", debug=debug
        )
        return cast(None, result)

    def delete_water_log(self, water_log_id: int, user_id: str = "-", debug: bool = False) -> None:
        """
        Deletes a water log entry.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/delete-water-log/

        Args:
            water_log_id: ID of the water log to delete
            user_id: Optional user ID, defaults to current user
        """
        result = self._make_request(
            f"foods/log/water/{water_log_id}.json",
            user_id=user_id,
            http_method="DELETE",
            debug=debug,
        )
        return cast(None, result)

    def get_food(self, food_id: int, debug: bool = False) -> JSONDict:
        """
        Retrieves details of a specific food from Fitbit's database or user's private foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-food/

        Args:
            food_id: ID of the food to retrieve
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Food details including nutritional information and available units

        Note:
            Nutritional values are only included for PRIVATE foods.
        """
        result = self._make_request(f"foods/{food_id}.json", requires_user_id=False, debug=debug)
        return cast(JSONDict, result)

    def get_food_goals(self, user_id: str = "-", debug: bool = False) -> JSONDict:
        """
        Retrieves the user's daily calorie consumption goal and/or food plan.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-food-goals/

        Args:
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Dict containing calorie goal and food plan if enabled

        Note:
            Food plan data is only included if the feature is enabled.
        """
        result = self._make_request("foods/log/goal.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    @validate_date_param(field_name="date")
    def get_food_log(self, date: str, user_id: str = "-", debug: bool = False) -> JSONDict:
        """
        Retrieves a summary of all food log entries for a given day.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-food-log/

        Args:
            date: The date in yyyy-MM-dd format or 'today'
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Dictionary containing food log entries and daily summary

        Raises:
            InvalidDateException: If date format is invalid
        """
        result = self._make_request(f"foods/log/date/{date}.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    def get_food_locales(self, debug: bool = False) -> JSONList:
        """
        Retrieves the list of food locales used for searching and creating foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-food-locales/
        debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            List of supported locales with regional settings
        """
        result = self._make_request("foods/locales.json", requires_user_id=False, debug=debug)
        return cast(JSONList, result)

    def get_food_units(self, debug: bool = False) -> JSONList:
        """
        Retrieves list of valid Fitbit food units.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-food-units/
        debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            List of available measurement units for food logging
        """
        result = self._make_request("foods/units.json", requires_user_id=False, debug=debug)
        return cast(JSONList, result)

    def get_frequent_foods(self, user_id: str = "-", debug: bool = False) -> JSONList:
        """
        Retrieves a list of user's frequently consumed foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-frequent-foods/

        Args:
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            List of frequently logged foods with serving information

        Note:
            Foods in the response can be quickly logged using create_food_log.
        """
        result = self._make_request("foods/log/frequent.json", user_id=user_id, debug=debug)
        return cast(JSONList, result)

    def get_recent_foods(self, user_id: str = "-", debug: bool = False) -> JSONList:
        """
        Retrieves a list of user's recently consumed foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-recent-foods/

        Args:
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            List of recently logged foods with dates and details
        """
        result = self._make_request("foods/log/recent.json", user_id=user_id, debug=debug)
        return cast(JSONList, result)

    def get_favorite_foods(self, user_id: str = "-", debug: bool = False) -> JSONDict:
        """
        Retrieves a list of user's favorite foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-favorite-foods/

        Args:
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            List of foods marked as favorites
        """
        result = self._make_request("foods/log/favorite.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    def get_meal(self, meal_id: int, user_id: str = "-", debug: bool = False) -> JSONDict:
        """
        Retrieves a single meal from user's food log.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-meal/

        Args:
            meal_id: ID of the meal to retrieve
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Meal details including constituent foods and nutritional info

        Note:
            All meals are associated with meal type "Anytime" (7).
        """
        result = self._make_request(f"meals/{meal_id}.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    def get_meals(self, user_id: str = "-", debug: bool = False) -> JSONDict:
        """
        Retrieves list of all user's saved meals.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-meals/

        Args:
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            List of saved meals with their foods and nutritional info
        """
        result = self._make_request("meals.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    def get_water_goal(self, user_id: str = "-", debug: bool = False) -> JSONDict:
        """
        Retrieves user's daily water consumption goal.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-water-goal/

        Args:
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Water goal amount and start date
        """
        result = self._make_request("foods/log/water/goal.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    @validate_date_param(field_name="date")
    def get_water_log(self, date: str, user_id: str = "-", debug: bool = False) -> JSONDict:
        """
        Retrieves water log entries for a specific date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-water-log/

        Args:
            date: Log date in yyyy-MM-dd format
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Water consumption summary and individual log entries

        Raises:
            InvalidDateException: If date format is invalid
        """
        result = self._make_request(
            f"foods/log/water/date/{date}.json", user_id=user_id, debug=debug
        )
        return cast(JSONDict, result)

    def search_foods(self, query: str, debug: bool = False) -> JSONDict:
        """
        Searches Fitbit's food database and user's custom foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/search-foods/

        Args:
            query: Search string to match against food names
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            List of matching foods with nutritional information

        Note:
            Results include both PUBLIC (Fitbit database) and PRIVATE (user-created) foods.
            Search uses the locale specified in accept-language header.  This can be
            specified when the client is initialized.
        """
        result = self._make_request(
            "foods/search.json", params={"query": query}, requires_user_id=False, debug=debug
        )
        return cast(JSONDict, result)

    def update_food_log(
        self,
        food_log_id: int,
        meal_type_id: MealType,
        unit_id: Optional[int] = None,
        amount: Optional[float] = None,
        calories: Optional[int] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
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
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Updated food log entry

        Note:
            Either (unit_id and amount) or calories must be provided.
            Only food logs with valid foodId can be updated with unit/amount.
        """
        params: ParamDict = {"mealTypeId": int(meal_type_id.value)}
        if unit_id is not None and amount is not None:
            params["unitId"] = unit_id
            params["amount"] = amount
        elif calories:
            params["calories"] = calories
        else:
            raise ValueError("Must provide either (unit_id and amount) or calories")

        result = self._make_request(
            f"foods/log/{food_log_id}.json",
            params=params,
            user_id=user_id,
            http_method="POST",
            debug=debug,
        )
        return cast(JSONDict, result)

    def update_meal(
        self,
        meal_id: int,
        name: str,
        description: str,
        foods: List[JSONDict],
        debug: bool = False,
        user_id: str = "-",
    ) -> JSONDict:
        """
        Updates an existing meal.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/update-meal/

        Args:
            meal_id: ID of the meal to update
            name: New name of the meal
            description: New short description of the meal
            foods: A list of dicts with the following entries (all required):
                food_id: ID of food to include in meal
                unit_id: ID of units used
                amount: Amount consumed (X.XX format)
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Updated meal information
        """
        foods = [{to_camel_case(k): v for k, v in d.items()} for d in foods]
        data = {"name": name, "description": description, "mealFoods": foods}
        result = self._make_request(
            f"meals/{meal_id}.json", json=data, user_id=user_id, http_method="POST", debug=debug
        )
        return cast(JSONDict, result)

    def update_water_log(
        self,
        water_log_id: int,
        amount: float,
        unit: Optional[WaterUnit] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """
        Updates an existing water log entry.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/update-water-log/

        Args:
            water_log_id: ID of the water log to update
            amount: New amount consumed (X.X format)
            unit: Optional unit ('ml', 'fl oz', 'cup')
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Updated water log entry

        Note:
            If unit is not specified, uses unit system from Accept-Language
            header.  This can be specified when the client is initialized.
        """
        params: ParamDict = {"amount": amount}
        if unit:
            params["unit"] = str(unit.value)
        result = self._make_request(
            f"foods/log/water/{water_log_id}.json",
            params=params,
            user_id=user_id,
            http_method="POST",
            debug=debug,
        )
        return cast(JSONDict, result)
