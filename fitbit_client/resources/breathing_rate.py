# fitbit_client/resources/breathing_rate.py

# Standard library imports
from typing import Any
from typing import Dict

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params


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

    @validate_date_param()
    def get_breathing_rate_summary_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Get breathing rate data for a single date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/breathing-rate/get-br-summary-by-date/

        Args:
            date: Date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Dict containing breathing rate data

        Raises:
            InvalidDateException: If date format is invalid

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
        return self._make_request(f"br/date/{date}.json", user_id=user_id, debug=debug)

    @validate_date_range_params(max_days=30)
    def get_breathing_rate_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Get breathing rate data for a date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/breathing-rate/get-br-summary-by-interval/

        Args:
            start_date: Start date in YYYY-MM-DD format or 'today'
            end_date: End date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Dict containing breathing rate data for the date range

        Raises:
            InvalidDateException: If date format is invalid
            InvalidDateRangeException: If date range exceeds 30 days or start_date is after end_date

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
        return self._make_request(
            f"br/date/{start_date}/{end_date}.json", user_id=user_id, debug=debug
        )
