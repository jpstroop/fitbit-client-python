# fitbit_client/resources/breathingrate.py

# Standard library imports
from datetime import datetime
from typing import Any
from typing import Dict

# Local imports
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.base import BaseResource


class BreathingRateResource(BaseResource):
    """
    Handles Fitbit Breathing Rate API endpoints for retrieving breathing rate measurements.

    Breathing Rate (also called Respiratory Rate) provides measurements of average breaths
    per minute during sleep. Data is collected during the user's "main sleep" period -
    the longest single period of sleep on a given date.

    Important Notes:
        - Data is only collected during sleep periods of at least 3 hours
        - Data is only processed when the user is still
        - Data becomes available ~15 minutes after device sync
        - Data is tied to the "main sleep" period (longest sleep period)
        - Sleep periods may span across midnight, so data might reflect previous day's sleep

    API Reference: https://dev.fitbit.com/build/reference/web-api/breathing-rate/
    """

    def _validate_date(self, date: str, field_name: str = "date") -> None:
        """Helper method to validate date format"""
        if date != "today":
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError as e:
                raise ValidationException(
                    message=f"Invalid date format: {str(e)}",
                    status_code=400,
                    error_type="validation",
                    field_name=field_name,
                )

    def get_breathing_rate_summary_by_date(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Get breathing rate data for a single date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/breathing-rate/get-br-summary-by-date/

        Args:
            date: Date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user

        Returns:
            Dict containing breathing rate data

        Raises:
            ValidationException: If date format is invalid

        Note:
            Data is collected during the user's main sleep period (longest sleep period).
            The measurement may reflect sleep that began the previous day.
            For example, requesting data for 2021-12-22 may include measurements
            from sleep that started on 2021-12-21.

            Additional requirements for breathing rate data:
            - At least 3 hours of sleep
            - User must be relatively still
            - Device must be synced
            - ~15 minute processing time after sync
        """
        self._validate_date(date)
        return self._make_request(f"br/date/{date}.json", user_id=user_id)

    def get_breathing_rate_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Get breathing rate data for a date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/breathing-rate/get-br-summary-by-interval/

        Args:
            start_date: Start date in YYYY-MM-DD format or 'today'
            end_date: End date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user

        Returns:
            Dict containing breathing rate data for the date range

        Raises:
            ValidationException: If date format is invalid, date range exceeds 30 days,
                               or start_date is after end_date

        Note:
            Maximum date range is 30 days.
            Data is collected during each day's main sleep period (longest sleep period).
            The measurement may reflect sleep that began the previous day.

            Additional requirements for breathing rate data:
            - At least 3 hours of sleep
            - User must be relatively still
            - Device must be synced
            - ~15 minute processing time after sync
        """
        # Validate date formats
        self._validate_date(start_date, "start_date")
        self._validate_date(end_date, "end_date")

        # Convert dates for comparison if not 'today'
        start = (
            datetime.now() if start_date == "today" else datetime.strptime(start_date, "%Y-%m-%d")
        )
        end = datetime.now() if end_date == "today" else datetime.strptime(end_date, "%Y-%m-%d")

        # Validate date order
        if start > end:
            raise ValidationException(
                message="Start date must be before or equal to end date",
                status_code=400,
                error_type="validation",
                field_name="date_range",
            )

        # Validate date range if both dates are specified
        if start_date != "today" and end_date != "today":
            date_diff = (end - start).days
            if date_diff > 30:
                raise ValidationException(
                    message="Maximum date range is 30 days",
                    status_code=400,
                    error_type="validation",
                    field_name="date_range",
                )

        return self._make_request(f"br/date/{start_date}/{end_date}.json", user_id=user_id)

    def get_breathing_rate_intraday_by_date(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        raise NotImplementedError

    def get_breathing_rate_intraday_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        raise NotImplementedError
