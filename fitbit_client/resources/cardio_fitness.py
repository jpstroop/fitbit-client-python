# fitbit_client/resources/cardio_fitness.py

# Standard library imports
from datetime import datetime
from typing import Any
from typing import Dict

# Local imports
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.base import BaseResource


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
            date: Date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user

        Returns:
            VO2 max data for the specified date

        Raises:
            ValidationException: If date format is invalid

        Note:
            Values may change throughout the day based on activity levels, heart rate,
            weight changes and other factors. The response always uses ml/kg/min units
            regardless of the Accept-Language header.
        """
        if date != "today":
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError as e:
                raise ValidationException(
                    message=f"Invalid date format: {str(e)}",
                    status_code=400,
                    error_type="validation",
                    field_name="date",
                )

        return self._make_request(f"cardioscore/date/{date}.json", user_id=user_id)

    def get_vo2_max_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Get cardio fitness (VO2 Max) data for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format or "today"
            end_date: End date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user

        Returns:
            VO2 max data for each date in the range

        Raises:
            ValidationException: If date format is invalid or date range exceeds 30 days

        Note:
            Maximum date range is 30 days.
            Values may change throughout the day based on activity levels, heart rate,
            weight changes and other factors. The response always uses ml/kg/min units
            regardless of the Accept-Language header.
        """
        try:
            if start_date != "today":
                start = datetime.strptime(start_date, "%Y-%m-%d")
            if end_date != "today":
                end = datetime.strptime(end_date, "%Y-%m-%d")

            if start_date != "today" and end_date != "today":
                date_diff = (end - start).days
                if date_diff > 30:
                    raise ValidationException(
                        message="Maximum date range is 30 days",
                        status_code=400,
                        error_type="validation",
                        field_name="date_range",
                    )
        except ValueError as e:
            raise ValidationException(
                message=f"Invalid date format: {str(e)}",
                status_code=400,
                error_type="validation",
                field_name="date",
            )

        return self._make_request(f"cardioscore/date/{start_date}/{end_date}.json", user_id=user_id)
