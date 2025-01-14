# resources/nutrition.py
from resources.base import BaseResource
from typing import Any
from typing import Dict
from typing import List
from typing import Optional


class NutritionResource(BaseResource):
    """
    Handles Fitbit Nutrition/Food API endpoints
    API Reference: https://dev.fitbit.com/build/reference/web-api/food-logging/
    """

    def get_food_logs(self, date_str: str = "today", user_id: str = "-") -> Dict[str, Any]:
        """
        Get food logs for a specific date.

        Parameters:
            date_str: Date in YYYY-MM-DD format or "today"
        """
        return self._get(f"foods/log/date/{date_str}.json", user_id=user_id)

    def log_food(
        self,
        food_id: Optional[int] = None,
        meal_type_id: int = 1,
        unit_id: Optional[int] = None,
        amount: float = 1,
        date: str = "today",
        food_name: Optional[str] = None,
        calories: Optional[int] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Log food to a user's food log.

        Parameters:
            food_id: Fitbit food ID (if logging a food from Fitbit's database)
            meal_type_id: 1=Breakfast, 2=Morning Snack, 3=Lunch, 4=Afternoon Snack,
                         5=Dinner, 7=Anytime
            unit_id: Unit ID from Fitbit's database
            amount: Number of units consumed
            date: Log date in YYYY-MM-DD format or "today"
            food_name: Custom food name (if not using food_id)
            calories: Calories in the portion (if not using food_id)
        """
        data = {"mealTypeId": meal_type_id, "amount": amount, "date": date}

        if food_id:
            data["foodId"] = food_id
            if unit_id:
                data["unitId"] = unit_id
        elif food_name and calories:
            data["foodName"] = food_name
            data["calories"] = calories
        else:
            raise ValueError("Must provide either food_id or (food_name and calories)")

        return self._post("foods/log.json", data=data, user_id=user_id)

    def delete_food_log(self, food_log_id: str, user_id: str = "-") -> None:
        """Delete a specific food log entry."""
        self._delete(f"foods/log/{food_log_id}.json", user_id=user_id)

    def get_recent_foods(self, user_id: str = "-") -> List[Dict[str, Any]]:
        """Get recently logged foods."""
        return self._get("foods/recent.json", user_id=user_id)

    def get_frequent_foods(self, user_id: str = "-") -> List[Dict[str, Any]]:
        """Get frequently logged foods."""
        return self._get("foods/frequent.json", user_id=user_id)

    def get_favorite_foods(self, user_id: str = "-") -> List[Dict[str, Any]]:
        """Get user's favorite foods."""
        return self._get("foods/log/favorite.json", user_id=user_id)

    def add_favorite_food(self, food_id: str, user_id: str = "-") -> Dict[str, Any]:
        """Add a food to user's favorites."""
        return self._post(f"foods/log/favorite/{food_id}.json", user_id=user_id)

    def get_meal_types(self) -> List[Dict[str, Any]]:
        """Get list of available meal types."""
        return self._get("foods/units.json")

    def search_foods(self, query: str) -> List[Dict[str, Any]]:
        """
        Search Fitbit food database.

        Parameters:
            query: Search string for food name
        """
        return self._get("foods/search.json", params={"query": query})

    def get_food_units(self) -> List[Dict[str, Any]]:
        """Get list of available food units."""
        return self._get("foods/units.json")

    def get_water_logs(self, date_str: str = "today", user_id: str = "-") -> Dict[str, Any]:
        """
        Get water logs for a specific date.

        Parameters:
            date_str: Date in YYYY-MM-DD format or "today"
        """
        return self._get(f"foods/log/water/date/{date_str}.json", user_id=user_id)

    def log_water(self, amount: float, unit: str = "fl oz", date: str = "today", user_id: str = "-") -> Dict[str, Any]:
        """
        Log water consumption.

        Parameters:
            amount: Amount of water consumed
            unit: Unit of measurement ('ml', 'fl oz', 'cup')
            date: Log date in YYYY-MM-DD format or "today"
        """
        data = {"amount": amount, "date": date, "unit": unit}
        return self._post("foods/log/water.json", data=data, user_id=user_id)
