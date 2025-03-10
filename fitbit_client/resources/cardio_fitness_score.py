# fitbit_client/resources/cardio_fitness_score.py

# Standard library imports
from typing import cast

# Local imports
from fitbit_client.resources._base import BaseResource
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params
from fitbit_client.utils.types import JSONDict


class CardioFitnessScoreResource(BaseResource):
    """Provides access to Fitbit Cardio Fitness Score (VO2 Max) API for cardiovascular fitness data.

    This resource handles endpoints for retrieving cardio fitness scores (VO2 Max), which
    represent the maximum rate at which the heart, lungs, and muscles can effectively use
    oxygen during exercise. Higher values generally indicate better cardiovascular fitness.

    Fitbit estimates VO2 Max based on resting heart rate, exercise heart rate response,
    age, gender, weight, and (when available) GPS-tracked runs. The API provides access
    to both single-day and multi-day data.

    API Reference: https://dev.fitbit.com/build/reference/web-api/cardio-fitness-score/

    Required Scopes:
        - cardio_fitness (for all cardio fitness endpoints)

    Note:
        - Values are always returned in ml/kg/min regardless of the user's unit preferences
        - Values may be returned either as a range (if no run data is available)
          or as a single numeric value (if the user uses GPS for runs)
        - For most users, cardio fitness scores typically range from 30-60 ml/kg/min
        - Not all Fitbit devices support cardio fitness score measurements
        - Scores may change throughout the day based on activity levels, heart rate,
          weight changes, and other factors
        - Data becomes available approximately 15 minutes after device sync
    """

    @validate_date_param()
    def get_vo2_max_summary_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Returns cardio fitness (VO2 Max) data for a single date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/cardio-fitness-score/get-vo2max-summary-by-date/

        Args:
            date: Date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: VO2 max data for the specified date (either a precise value or a range)

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid

        Note:
            - Values are always reported in ml/kg/min units
            - If the user has GPS run data, a single "vo2Max" value is returned
            - If no GPS run data is available, a "vo2MaxRange" with "low" and "high" values is returned
            - A missing date in the response means no cardio score was calculated that day
            - Scores may change throughout the day based on activity levels and heart rate
            - Higher values (typically 40-60 ml/kg/min) indicate better cardiovascular fitness
        """
        result = self._make_request(f"cardioscore/date/{date}.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    @validate_date_range_params(max_days=30)
    def get_vo2_max_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Returns cardio fitness (VO2 Max) data for a specified date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/cardio-fitness-score/get-vo2max-summary-by-interval/

        Args:
            start_date: Start date in YYYY-MM-DD format or "today"
            end_date: End date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: VO2 max data for each date in the specified range

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.InvalidDateRangeException: If date range exceeds 30 days
                or start_date is after end_date

        Note:
            - Maximum date range is 30 days
            - Values are always reported in ml/kg/min units
            - Response may include a mix of exact values and ranges, depending on available data
            - Days without a cardio fitness score will not appear in the results
            - Each day's entry may contain either:
              * "vo2Max": A precise measurement (if GPS run data is available)
              * "vo2MaxRange": A range with "low" and "high" values (if no GPS data)
            - The data is particularly useful for tracking cardiovascular fitness changes over time
        """
        result = self._make_request(
            f"cardioscore/date/{start_date}/{end_date}.json", user_id=user_id, debug=debug
        )
        return cast(JSONDict, result)
