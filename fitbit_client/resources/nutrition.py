# fitbit_client/resources/nutrition.py

# Standard library imports
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from typing import cast

# Local imports
from fitbit_client.exceptions import ClientValidationException
from fitbit_client.exceptions import MissingParameterException
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
    """Provides access to Fitbit Nutrition API for managing food and water tracking.

    This resource handles endpoints for logging food intake, creating and managing custom foods
    and meals, tracking water consumption, setting nutritional goals, and retrieving food
    database information. It supports comprehensive tracking of dietary intake and hydration.

    API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/

    Required Scopes:
      - nutrition: Required for all endpoints in this resource

    Note:
        The Nutrition API is one of the most comprehensive Fitbit APIs, with functionality for:
        - Logging foods and water consumption
        - Creating custom foods and meals
        - Managing favorites and frequently used items
        - Searching the Fitbit food database
        - Setting and retrieving nutritional goals
        - Retrieving nutritional unit information

        Nutrition data is always associated with a specific date, and most logging
        endpoints require a valid foodId from either the Fitbit food database or
        from custom user-created food entries. Meals are collections of food entries
        that can be reused for convenience.

        All nutritional values are specified in the units set in the user's Fitbit
        account settings (metric or imperial).
    """

    def add_favorite_foods(self, food_id: int, user_id: str = "-", debug: bool = False) -> None:
        """
        Adds a food to the user's list of favorite foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/add-favorite-foods/

        Args:
            food_id: ID of the food to add to favorites (from Fitbit's food database)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            None: This endpoint returns an empty response on success

        Raises:
            fitbit_client.exceptions.ValidationException: If the food ID is invalid or already a favorite
            fitbit_client.exceptions.NotFoundException: If the food ID doesn't exist

        Note:
            Favorite foods are displayed prominently when logging meals, making
            it easier to log frequently consumed items.
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
        """Creates a new private custom food entry for a user.

        This endpoint allows users to create their own custom food entries that can be
        reused when logging meals. Custom foods are private to the user's account and
        include detailed nutritional information.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/create-food/

        Args:
            name: Name of the food being created
            default_food_measurement_unit_id: ID from the food units endpoint (get_food_units)
            default_serving_size: Size of default serving with nutritional values
            calories: Number of calories for default serving size
            description: Description of the food
            form_type: Food texture - either FoodFormType.LIQUID or FoodFormType.DRY
            nutritional_values: Dictionary mapping NutritionalValue constants to their amounts
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Created food entry details containing the food object with ID, name, nutritional values,
                  and other metadata about the custom food

        Raises:
            fitbit_client.exceptions.ValidationException: If required parameters are invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            The nutritional_values dictionary accepts any nutrition constants defined in
            the NutritionalValue enum, including macronutrients (protein, carbs, fat) and
            micronutrients (vitamins, minerals). Values should be provided in the units
            specified in the user's account settings.

            Food measurement unit IDs can be retrieved using the get_food_units method.
            Common values include:
            - 226: gram
            - 180: ounce
            - 147: tablespoon
            - 328: milliliter
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
                message="Calories from fat must be an integer", field_name="CALORIES_FROM_FAT"
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
        """Creates a food log entry for tracking nutrition on a specific day.

        This endpoint allows recording food consumption either from the Fitbit food database
        or as a custom food entry with nutritional information.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/create-food-log/

        Args:
            date: Log date in YYYY-MM-DD format or 'today'
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
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Created food log entry containing the food details, nutritional values,
                  and a summary of the day's total nutritional intake

        Raises:
            fitbit_client.exceptions.ClientValidationException: Must provide either food_id or (food_name and calories)
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            There are two ways to log foods:
            1. Using food_id from the Fitbit database: Provide food_id, unit_id, and amount
            2. Custom food entry: Provide food_name, calories, unit_id, and amount

            The favorite parameter (when set to True) will automatically add the food
            to the user's favorites list when using a food_id.

            For custom food entries, you can optionally provide:
            - brand_name: To specify the brand of the food
            - nutritional_values: To specify detailed nutritional information

            The unit_id must match one of the units associated with the food. For
            existing foods, valid units can be found in the food details. For custom
            foods, any valid unit ID from the get_food_units method can be used.

            The response includes both the created food log entry and a summary of
            the day's nutritional totals after adding this entry.
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
        """Creates or updates a user's daily calorie consumption goal or food plan.

        This endpoint allows setting either a simple calorie goal or a more complex
        food plan linked to weight management goals.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/create-food-goal/

        Args:
            calories: Optional manual calorie consumption goal
            intensity: Optional food plan intensity (MAINTENANCE, EASIER, MEDIUM,
                      KINDAHARD, HARDER)
            personalized: Optional food plan type (true/false)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Updated food goal information containing calorie goals and food plan details
                  (if enabled)

        Raises:
            fitbit_client.exceptions.MissingParameterException: If neither calories nor intensity is provided
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted
            fitbit_client.exceptions.ValidationException: If parameters are invalid

        Note:
            There are two ways to set nutrition goals:
            1. Simple calorie goal: Provide only the calories parameter
            2. Food plan: Provide the intensity parameter, with optional personalized parameter

            A food plan is linked to weight management and requires an active weight goal
            to be set using the create_weight_goal method in the BodyResource.

            The food plan intensity levels determine calorie deficit or surplus:
            - MAINTENANCE: Maintain current weight
            - EASIER: Small deficit/surplus for gradual change
            - MEDIUM: Moderate deficit/surplus for steady change
            - KINDAHARD: Large deficit/surplus for faster change
            - HARDER: Maximum recommended deficit/surplus

            The personalized parameter, when set to true, creates a food plan that
            accounts for the user's activity levels rather than a fixed calorie goal.
        """
        if not calories and not intensity:
            raise MissingParameterException(
                message="Must provide either calories or intensity", field_name="calories/intensity"
            )

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
        """Creates a reusable meal template with the specified foods.

        This endpoint creates a saved meal template that can be used for easier
        logging of frequently consumed food combinations.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/create-meal/

        Args:
            name: Name of the meal
            description: Short description of the meal
            foods: A list of dicts with the following entries (all required):
                food_id: ID of food to include in meal
                unit_id: ID of units used
                amount: Amount consumed (X.XX format)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Created meal details containing the meal's ID, name, description, and the
                  list of foods included in the meal

        Raises:
            fitbit_client.exceptions.ValidationException: If food objects are incorrectly formatted
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Meals are simply templates that can be reused for easier logging.
            Creating a meal does not automatically log those foods to any date.
            To log these foods on a specific date, you must still use create_food_log
            for each food item in the meal.

            Meals are always associated with meal type "Anytime" (7) when created,
            but individual foods can be assigned to specific meal types when logged.

            Each food object in the foods list requires:
            - food_id: Identifier for the food from the Fitbit database or custom foods
            - unit_id: Unit identifier (see get_food_units for available options)
            - amount: Quantity in specified units

            Food IDs can be obtained from food search results or the user's custom foods.
        """
        # snakes to camels
        foods_list = [{to_camel_case(k): v for k, v in d.items()} for d in foods]
        # Use cast to handle the complex structure
        data_dict = {"name": name, "description": description, "mealFoods": foods_list}
        result = self._make_request(
            "meals.json",
            json=cast(JSONDict, data_dict),
            user_id=user_id,
            http_method="POST",
            debug=debug,
        )
        return cast(JSONDict, result)

    def create_water_goal(self, target: float, user_id: str = "-", debug: bool = False) -> JSONDict:
        """Creates or updates a user's daily water consumption goal.

        This endpoint sets a target for daily water intake, which is used to track
        hydration progress in the Fitbit app.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/create-water-goal/

        Args:
            target: Target water goal in the unit system matching locale (mL or fl oz)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Updated water goal information containing the target amount and start date

        Raises:
            fitbit_client.exceptions.ValidationException: If the target value is not positive
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            The target value should be specified in the unit system that corresponds
            to the Accept-Language header provided during client initialization
            (fluid ounces for en_US, milliliters for most other locales).

            Typical daily water intake recommendations range from 1500-3000mL
            (50-100 fl oz) depending on factors like body weight, activity level,
            and climate.

            Progress toward this goal can be tracked by logging water consumption
            using the create_water_log method.
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
        """Creates a water log entry for tracking hydration on a specific day.

        This endpoint allows recording water consumption for a given date, which
        contributes to the user's daily hydration tracking.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/create-water-log/

        Args:
            amount: Amount of water consumed (X.X format)
            date: Log date in YYYY-MM-DD format or 'today'
            unit: Optional unit (WaterUnit.ML, WaterUnit.FL_OZ, or WaterUnit.CUP)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Created water log entry containing amount, ID, date, and unit information
                  (if unit was explicitly provided)

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.ValidationException: If amount format is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Water logs track hydration over time and contribute to daily water totals.
            Multiple entries can be logged on the same day to track water consumption
            throughout the day.

            If unit is not specified, the API uses the unit system from the Accept-Language
            header which can be specified when the client is initialized:
            - For en_US locale: fluid ounces (fl oz)
            - For other locales: milliliters (mL)

            Available water units from the WaterUnit enum:
            - WaterUnit.ML: milliliters (metric)
            - WaterUnit.FL_OZ: fluid ounces (imperial)
            - WaterUnit.CUP: cups (common)

            Water logs contribute to the daily water total shown in the Fitbit app and
            progress toward any water goal set using create_water_goal.
        """
        params: ParamDict = {"amount": amount, "date": date}
        if unit:
            params["unit"] = str(unit.value)
        result = self._make_request(
            "foods/log/water.json", params=params, user_id=user_id, http_method="POST", debug=debug
        )
        return cast(JSONDict, result)

    def delete_custom_food(self, food_id: int, user_id: str = "-", debug: bool = False) -> None:
        """Deletes a custom food permanently from the user's account.

        This endpoint permanently removes a custom food that was previously created
        by the user. This cannot be used to delete foods from the Fitbit database.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/delete-custom-food/

        Args:
            food_id: ID of the custom food to delete
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            None: This endpoint returns an empty response on success

        Raises:
            fitbit_client.exceptions.NotFoundException: If the food ID doesn't exist
            fitbit_client.exceptions.ValidationException: If attempting to delete a non-custom food
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Only custom foods created by the user (accessLevel: "PRIVATE") can be deleted.
            Foods from the Fitbit database (accessLevel: "PUBLIC") cannot be deleted.

            Deleting a custom food will also remove it from favorites if it was marked
            as a favorite. Any existing food logs using this food will remain intact,
            but you won't be able to create new logs with this food ID.

            Custom food IDs can be obtained from the search_foods method or from
            previously created custom foods using create_food.
        """
        result = self._make_request(
            f"foods/{food_id}.json", user_id=user_id, http_method="DELETE", debug=debug
        )
        return cast(None, result)

    def delete_favorite_foods(self, food_id: int, user_id: str = "-", debug: bool = False) -> None:
        """Removes a food from the user's list of favorite foods.

        This endpoint removes a food from the user's favorites list without
        deleting the food itself from the database.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/delete-favorite-foods/

        Args:
            food_id: ID of the food to remove from favorites
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            None: This endpoint returns an empty response on success

        Raises:
            fitbit_client.exceptions.NotFoundException: If the food ID doesn't exist
            fitbit_client.exceptions.ValidationException: If the food isn't in favorites
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            This endpoint only removes the food from the favorites list. The food itself
            (whether from the Fitbit database or a custom food) remains available for
            logging. This affects which foods appear in the favorites section of the
            Fitbit app when logging meals.

            Foods can be added to favorites using the add_favorite_foods method or
            by setting the favorite parameter to True when using create_food_log.

            Food IDs can be obtained from the get_favorite_foods, search_foods,
            get_frequent_foods, or get_recent_foods methods.
        """
        result = self._make_request(
            f"foods/log/favorite/{food_id}.json", user_id=user_id, http_method="DELETE", debug=debug
        )
        return cast(None, result)

    delete_favorite_food = delete_favorite_foods  # semantically correct alias

    def delete_food_log(self, food_log_id: int, user_id: str = "-", debug: bool = False) -> None:
        """Deletes a food log entry permanently.

        This endpoint permanently removes a specific food log entry from the user's
        food diary for a particular date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/delete-food-log/

        Args:
            food_log_id: ID of the food log to delete
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            None: This endpoint returns an empty response on success

        Raises:
            fitbit_client.exceptions.NotFoundException: If the food log ID doesn't exist
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Deleting a food log entry removes it from the daily total calculations and
            nutritional summaries for that day. The deletion is permanent and cannot be undone.

            This operation deletes a specific food log entry (a record of consuming a
            food on a particular date), not the food itself from the database.

            Food log IDs can be obtained from the get_food_log method, which returns
            all food logs for a specific date.
        """
        result = self._make_request(
            f"foods/log/{food_log_id}.json", user_id=user_id, http_method="DELETE", debug=debug
        )
        return cast(None, result)

    def delete_meal(self, meal_id: int, user_id: str = "-", debug: bool = False) -> None:
        """Deletes a meal template permanently.

        This endpoint permanently removes a meal template from the user's saved meals.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/delete-meal/

        Args:
            meal_id: ID of the meal to delete
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            None: This endpoint returns an empty response on success

        Raises:
            fitbit_client.exceptions.NotFoundException: If the meal ID doesn't exist
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Meal templates are simply collections of foods that can be reused for
            easier logging. Deleting a meal template does not affect any food logs
            that may have been previously created using that meal.

            This operation removes the meal template itself, not the constituent foods
            from the database.

            Meal IDs can be obtained from the get_meals method, which returns
            all saved meal templates for the user.
        """
        result = self._make_request(
            f"meals/{meal_id}.json", user_id=user_id, http_method="DELETE", debug=debug
        )
        return cast(None, result)

    def delete_water_log(self, water_log_id: int, user_id: str = "-", debug: bool = False) -> None:
        """Deletes a water log entry permanently.

        This endpoint permanently removes a specific water log entry from the user's
        hydration tracking for a particular date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/delete-water-log/

        Args:
            water_log_id: ID of the water log to delete
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            None: This endpoint returns an empty response on success

        Raises:
            fitbit_client.exceptions.NotFoundException: If the water log ID doesn't exist
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Deleting a water log entry removes it from the daily hydration total calculations
            for that day. The deletion is permanent and cannot be undone.

            This affects progress toward any water goal that may be set for the user.

            Water log IDs can be obtained from the get_water_log method, which returns
            all water logs for a specific date.
        """
        result = self._make_request(
            f"foods/log/water/{water_log_id}.json",
            user_id=user_id,
            http_method="DELETE",
            debug=debug,
        )
        return cast(None, result)

    def get_food(self, food_id: int, debug: bool = False) -> JSONDict:
        """Returns details of a specific food from Fitbit's database or user's private foods.

        This endpoint retrieves comprehensive information about a food item, including
        nutritional values, serving sizes, and brand information. It can be used to retrieve
        both public foods from Fitbit's database and private custom foods created by the user.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-food/

        Args:
            food_id: ID of the food to retrieve
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Food details containing name, brand, calories, available units, and nutritional
                  values (for private foods only)

        Raises:
            fitbit_client.exceptions.NotFoundException: If the food ID doesn't exist
            fitbit_client.exceptions.AuthorizationException: If the user lacks permission to access the food
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Nutritional values are only included for PRIVATE (custom) foods.
            For foods from the Fitbit database, only basic information is provided.

            Food IDs are unique across both the Fitbit database and user's private foods.
            These IDs are used when logging food consumption with the create_food_log method.

            This endpoint is public and does not require a user_id parameter.
        """
        result = self._make_request(f"foods/{food_id}.json", requires_user_id=False, debug=debug)
        return cast(JSONDict, result)

    def get_food_goals(self, user_id: str = "-", debug: bool = False) -> JSONDict:
        """Retrieves the user's daily calorie consumption goal and/or food plan.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-food-goals/

        Args:
            user_id: Optional user ID, defaults to current user
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Food goal information containing calorie goals and food plan details (if enabled)

        Raises:
            fitbit_client.exceptions.AuthorizationException: If not authorized for the nutrition scope
            fitbit_client.exceptions.InvalidRequestException: If the user ID is invalid

        Note:
            Food plan data is only included if the feature is enabled.
            The food plan is tied to the user's weight goals and activity level.
        """
        result = self._make_request("foods/log/goal.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    @validate_date_param(field_name="date")
    def get_food_log(self, date: str, user_id: str = "-", debug: bool = False) -> JSONDict:
        """Retrieves a summary of all food log entries for a given day.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-food-log/

        Args:
            date: The date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Food log data containing an array of logged foods, nutritional goals, and
                  a summary of the day's total nutritional values

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid

        Note:
            The response includes both individual food entries grouped by meal type
            and a daily summary of total nutritional values. Each food entry contains
            both the logged food details and its nutritional contribution to the daily total.
        """
        result = self._make_request(f"foods/log/date/{date}.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    def get_food_locales(self, debug: bool = False) -> JSONList:
        """Retrieves the list of food locales used for searching and creating foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-food-locales/

        Args:
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONList: List of supported locales with country name, language, and locale identifier

        Raises:
            fitbit_client.exceptions.AuthorizationException: If not authorized for the nutrition scope
            fitbit_client.exceptions.ServiceUnavailableException: If the Fitbit service is unavailable

        Note:
            Locale settings affect food database searches and the units used for
            nutritional values. The selected locale determines which regional
            food database is used for searches and which measurement system
            (metric or imperial) is used for logging values.
        """
        result = self._make_request("foods/locales.json", requires_user_id=False, debug=debug)
        return cast(JSONList, result)

    def get_food_units(self, debug: bool = False) -> JSONList:
        """Retrieves list of valid Fitbit food units.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-food-units/

        Args:
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONList: List of available food measurement units with their IDs, names, and plural forms

        Raises:
            fitbit_client.exceptions.AuthorizationException: If not authorized for the nutrition scope
            fitbit_client.exceptions.ServiceUnavailableException: If the Fitbit service is unavailable

        Note:
            Unit IDs are used in several nutrition endpoints, including:
            - create_food: For specifying default measurement units for custom foods
            - create_food_log: For specifying the measurement units for logged food quantities
            - update_food_log: For changing the measurement units of existing logs

            Common unit IDs include:
            - Weight units: 226 (gram), 180 (ounce)
            - Volume units: 328 (milliliter), 218 (fluid ounce), 147 (tablespoon),
                          182 (cup), 189 (pint), 204 (quart)
            - Count units: 221 (serving)
        """
        result = self._make_request("foods/units.json", requires_user_id=False, debug=debug)
        return cast(JSONList, result)

    def get_frequent_foods(self, user_id: str = "-", debug: bool = False) -> JSONList:
        """Retrieves a list of user's frequently consumed foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-frequent-foods/

        Args:
            user_id: Optional user ID, defaults to current user
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONList: List of frequently logged foods with details including food ID, name, brand,
                  calories, and available measurement units

        Raises:
            fitbit_client.exceptions.AuthorizationException: If not authorized for the nutrition scope
            fitbit_client.exceptions.InvalidRequestException: If the user ID is invalid

        Note:
            The frequent foods endpoint returns foods that the user has logged
            multiple times, making it easier to quickly log commonly consumed items.

            Each food entry contains essential information needed for logging, including:
            - Food identification (foodId, name, brand)
            - Calorie information
            - Available measurement units
            - Default unit for serving size

            These foods can be efficiently logged using the create_food_log method
            with their foodId values.
        """
        result = self._make_request("foods/log/frequent.json", user_id=user_id, debug=debug)
        return cast(JSONList, result)

    def get_recent_foods(self, user_id: str = "-", debug: bool = False) -> JSONList:
        """Retrieves a list of user's recently consumed foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-recent-foods/

        Args:
            user_id: Optional user ID, defaults to current user
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONList: List of recently logged foods with details including food ID, log ID, name,
                  brand, calories, log date, and available measurement units

        Raises:
            fitbit_client.exceptions.AuthorizationException: If not authorized for the nutrition scope
            fitbit_client.exceptions.InvalidRequestException: If the user ID is invalid

        Note:
            The recent foods endpoint returns foods that the user has most recently
            logged, sorted with the most recent entries first. Unlike the frequent
            foods endpoint, this includes one-time or infrequently consumed items.

            Each food entry includes both the food details needed for logging again
            (foodId, name, units) and information about the previous log (logId, logDate).

            These foods can be efficiently logged again using the create_food_log method
            with their foodId values.
        """
        result = self._make_request("foods/log/recent.json", user_id=user_id, debug=debug)
        return cast(JSONList, result)

    def get_favorite_foods(self, user_id: str = "-", debug: bool = False) -> JSONDict:
        """Retrieves a list of user's favorite foods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-favorite-foods/

        Args:
            user_id: Optional user ID, defaults to current user
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Dictionary containing an array of the user's favorite foods with their
                  details including name, brand, calories, and available units

        Raises:
            fitbit_client.exceptions.AuthorizationException: If not authorized to access this data
            fitbit_client.exceptions.InvalidRequestException: If the request parameters are invalid

        Note:
            Favorite foods are those explicitly marked as favorites by the user
            using the add_favorite_foods method. These are displayed prominently
            in the Fitbit app and are intended to provide quick access to frequently
            used items.

            Foods can be added to favorites with the add_favorite_foods method and
            removed with delete_favorite_foods. When logging foods with create_food_log,
            the favorite parameter can be used to automatically add a food to favorites.
        """
        result = self._make_request("foods/log/favorite.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    def get_meal(self, meal_id: int, user_id: str = "-", debug: bool = False) -> JSONDict:
        """Retrieves a single meal from user's food log.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-meal/

        Args:
            meal_id: ID of the meal to retrieve
            user_id: Optional user ID, defaults to current user
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Single meal details containing name, description, ID, and the list of
                  foods included in the meal with their amounts and nutritional information

        Raises:
            fitbit_client.exceptions.NotFoundException: If the meal ID doesn't exist
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Meals in Fitbit are user-defined collections of foods that can be logged
            together for convenience. All meals are associated with meal type "Anytime" (7),
            regardless of when they're consumed. When logging a meal, the individual
            food items can be assigned to specific meal types (breakfast, lunch, etc.).

            Meals can be created with the create_meal method, updated with update_meal,
            and deleted with delete_meal.
        """
        result = self._make_request(f"meals/{meal_id}.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    def get_meals(self, user_id: str = "-", debug: bool = False) -> JSONDict:
        """Retrieves list of all user's saved meals.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-meals/

        Args:
            user_id: Optional user ID, defaults to current user
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Dictionary containing an array of all user-defined meals with their details
                  and constituent foods

        Raises:
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Meals provide a way to save commonly eaten food combinations for
            easy logging. Unlike individual food logs which are associated with
            specific dates, meals are reusable templates that can be applied to
            any date when needed.

            Each meal has:
            - A unique ID for referencing in other API calls
            - A name and description for identification
            - A list of constituent foods with their amounts and units
            - Calorie information for each food component

            To log a meal on a specific date, you would need to individually log
            each food in the meal using the create_food_log method.
        """
        result = self._make_request("meals.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    def get_water_goal(self, user_id: str = "-", debug: bool = False) -> JSONDict:
        """Retrieves user's daily water consumption goal.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-water-goal/

        Args:
            user_id: Optional user ID, defaults to current user
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Water goal information containing the target amount and when the goal was set

        Raises:
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            The target value is expressed in the user's preferred unit system
            (milliliters for metric, fluid ounces for imperial), determined by
            the user's locale settings. The create_water_goal method can be used
            to update this target value.

            Water consumption is tracked separately from other nutrients but is
            included in the daily summary returned by get_food_log.
        """
        result = self._make_request("foods/log/water/goal.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    @validate_date_param(field_name="date")
    def get_water_log(self, date: str, user_id: str = "-", debug: bool = False) -> JSONDict:
        """Retrieves water log entries for a specific date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/get-water-log/

        Args:
            date: Log date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Water log data containing individual water entries and a summary of
                  total water consumption for the day

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Water logs represent individual entries of water consumption throughout
            the day. The summary provides the total amount for the day, while the
            water array contains each individual log entry.

            Amounts are expressed in the user's preferred unit system (milliliters for
            metric, fluid ounces for imperial), determined by the user's locale settings.

            Water logs can be created with create_water_log, updated with update_water_log,
            and deleted with delete_water_log.
        """
        result = self._make_request(
            f"foods/log/water/date/{date}.json", user_id=user_id, debug=debug
        )
        return cast(JSONDict, result)

    def search_foods(self, query: str, debug: bool = False) -> JSONDict:
        """Searches Fitbit's food database and user's custom foods.

        This endpoint allows searching both the Fitbit food database and the user's custom
        foods by name. The search results include basic nutritional information and can
        be used to retrieve food IDs for logging consumption.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/search-foods/

        Args:
            query: Search string to match against food names
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Dictionary containing an array of foods matching the search query, with
                  details including name, brand, calories, and available units

        Raises:
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Results include both PUBLIC (Fitbit database) and PRIVATE (user-created) foods.
            Search uses the locale specified in the Accept-Language header, which can be
            specified when the client is initialized.

            This endpoint is public and does not require a user_id parameter, but will
            still return PRIVATE foods for the authenticated user.

            The search results provide enough information to display basic food details,
            but for comprehensive nutritional information, use the get_food method with
            the returned foodId values.
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
        """Updates an existing food log entry.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/update-food-log/

        Args:
            food_log_id: ID of the food log to update
            meal_type_id: Meal type (BREAKFAST, MORNING_SNACK, LUNCH, etc.)
            unit_id: Optional unit ID (required for foods with foodId)
            amount: Optional amount in specified unit (required for foods with foodId)
            calories: Optional calories (only for custom food logs)
            user_id: Optional user ID, defaults to current user
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Updated food log entry containing the modified food details with updated
                  amount, calories, and nutritional values reflecting the changes

        Raises:
            fitbit_client.exceptions.MissingParameterException: If neither (unit_id and amount) nor calories are provided
            fitbit_client.exceptions.NotFoundException: If the food log ID doesn't exist
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Either (unit_id and amount) or calories must be provided:
            - For foods with a valid foodId, provide unit_id and amount to update the serving size
            - For custom food logs (without foodId), provide calories to update the calorie count

            This method allows changing the meal type (breakfast, lunch, etc.) for a food log
            entry as well as its quantity. The nutritional values are automatically recalculated
            based on the updated amount.

            Food log IDs can be obtained from the get_food_log method.
        """
        params: ParamDict = {"mealTypeId": int(meal_type_id.value)}
        if unit_id is not None and amount is not None:
            params["unitId"] = unit_id
            params["amount"] = amount
        elif calories:
            params["calories"] = calories
        else:
            raise MissingParameterException(
                message="Must provide either (unit_id and amount) or calories",
                field_name="unit_id/amount/calories",
            )

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
        """Updates an existing meal.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/update-meal/

        Args:
            meal_id: ID of the meal to update
            name: New name of the meal
            description: New short description of the meal
            foods: A list of dicts with the following entries (all required):
                food_id: ID of food to include in meal
                unit_id: ID of units used
                amount: Amount consumed (X.XX format)
            debug: If True, prints a curl command to stdout to help with debugging (default: False)
            user_id: Optional user ID, defaults to current user

        Returns:
            JSONDict: Updated meal information containing the modified meal details with name,
                  description, ID, and the updated list of foods

        Raises:
            fitbit_client.exceptions.NotFoundException: If the meal ID doesn't exist
            fitbit_client.exceptions.ValidationException: If food objects are incorrectly formatted
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            This method completely replaces the existing meal with the new definition.
            All foods must be specified in the foods list, even those that were previously
            part of the meal and should remain unchanged. Any foods not included in the
            update will be removed from the meal.

            Each food object in the foods list requires:
            - food_id: Identifier for the food from the Fitbit database or custom foods
            - unit_id: Unit identifier (see get_food_units for available options)
            - amount: Quantity in specified units

            Meal IDs can be obtained from the get_meals method. Updating a meal does not
            affect any food logs that were previously created using this meal.
        """
        foods_list = [{to_camel_case(k): v for k, v in d.items()} for d in foods]
        # Use cast to handle the complex structure
        data_dict = {"name": name, "description": description, "mealFoods": foods_list}
        result = self._make_request(
            f"meals/{meal_id}.json",
            json=cast(JSONDict, data_dict),
            user_id=user_id,
            http_method="POST",
            debug=debug,
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
        """Updates an existing water log entry.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition/update-water-log/

        Args:
            water_log_id: ID of the water log to update
            amount: New amount consumed (X.X format)
            unit: Optional unit ('ml', 'fl oz', 'cup')
            user_id: Optional user ID, defaults to current user
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Updated water log entry containing the modified amount, log ID, date,
                  and unit information (if unit was explicitly provided)

        Raises:
            fitbit_client.exceptions.NotFoundException: If the water log ID doesn't exist
            fitbit_client.exceptions.ValidationException: If amount format is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            If unit is not specified, the API uses the unit system from the Accept-Language
            header which can be specified when the client is initialized (metric or imperial).

            Available water units are defined in the WaterUnit enum:
            - WaterUnit.ML: milliliters (metric)
            - WaterUnit.FL_OZ: fluid ounces (imperial)
            - WaterUnit.CUP: cups (common)

            Water log IDs can be obtained from the get_water_log method.

            After updating a water log, the daily summary values are automatically recalculated
            to reflect the new hydration total.
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
