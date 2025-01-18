# resources/cardio_fitness.py
# Standard library imports
from typing import Any
from typing import Dict

# Local imports
from resources.base import BaseResource


class CardioFitnessResource(BaseResource):
    """
    Handles Fitbit Cardio Fitness (VO2 Max) API endpoints for accessing cardio fitness scores.

    Cardio Fitness Score (VO2 Max) represents the maximum rate at which the heart, lungs,
    and muscles can effectively use oxygen during exercise. The score is determined by
    resting heart rate, age, gender, weight, and other personal information.

    Values are always returned in ml/kg/min regardless of the units header. Values may be
    returned either as a range (if no run data is available) or as a single numeric value
    (if the user uses GPS for runs).

    API Reference: https://dev.fitbit.com/build/reference/web-api/cardio-fitness-score/
    """

    def get_vo2_max_summary_by_date(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Get cardio fitness (VO2 Max) data for a single date.

        Args:
            date: Date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user

        Note:
            Values may change throughout the day based on activity levels, heart rate,
            weight changes and other factors. The response always uses ml/kg/min units
            regardless of the Accept-Language header.
        """
        return self._get(f"cardioscore/date/{date}.json", user_id=user_id)

    def get_vo2_max_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Get cardio fitness (VO2 Max) data for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format or 'today'
            end_date: End date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user

        Note:
            Maximum date range is 30 days.
            Values may change throughout the day based on activity levels, heart rate,
            weight changes and other factors. The response always uses ml/kg/min units
            regardless of the Accept-Language header.
        """
        return self._get(f"cardioscore/date/{start_date}/{end_date}.json", user_id=user_id)
