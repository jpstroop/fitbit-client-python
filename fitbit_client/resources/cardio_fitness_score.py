# fitbit_client/resources/cardio_fitness_score.py

# Standard library imports
from typing import Dict
from typing import cast

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params
from fitbit_client.utils.types import JSONDict


class CardioFitnessScoreResource(BaseResource):
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

    @validate_date_param()
    def get_vo2_max_summary_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """
        Get cardio fitness (VO2 Max) data for a single date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/cardio-fitness-score/get-vo2max-summary-by-date/

        Args:
            date: Date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            VO2 max data for the specified date

        Raises:
            InvalidDateException: If date format is invalid

        Note:
            Values may change throughout the day based on activity levels, heart rate,
            weight changes and other factors. The response always uses ml/kg/min units
            regardless of the Accept-Language header.
        """
        result = self._make_request(f"cardioscore/date/{date}.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    @validate_date_range_params(max_days=30)
    def get_vo2_max_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """
        Get cardio fitness (VO2 Max) data for a date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/cardio-fitness-score/get-vo2max-summary-by-interval/

        Args:
            start_date: Start date in YYYY-MM-DD format or "today"
            end_date: End date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            VO2 max data for each date in the range

        Raises:
            InvalidDateException: If date format is invalid
            InvalidDateRangeException: If date range exceeds 30 days or start_date is after end_date

        Note:
            Maximum date range is 30 days.
            Values may change throughout the day based on activity levels, heart rate,
            weight changes and other factors. The response always uses ml/kg/min units
            regardless of the Accept-Language header.
        """
        result = self._make_request(
            f"cardioscore/date/{start_date}/{end_date}.json", user_id=user_id, debug=debug
        )
        return cast(JSONDict, result)
