# resources/breathingrate.py
# Standard library imports
from typing import Any
from typing import Dict

# Local imports
from resources.base import BaseResource


class BreathingRateResource(BaseResource):
    """
    Handles Fitbit Breathing Rate API endpoints for retrieving breathing rate measurements.

    Breathing Rate (also called Respiratory Rate) provides measurements of average breaths
    per minute during sleep. Data is collected during the user's "main sleep" period -
    the longest single period of sleep on a given date.

    API Reference: https://dev.fitbit.com/build/reference/web-api/breathing-rate/
    """

    def get_breathing_rate_summary_by_date(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Get breathing rate data for a single date.

        Args:
            date: Date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user

        Note:
            Data is collected during the user's main sleep period (longest sleep period).
            The measurement may reflect sleep that began the previous day.
            For example, requesting data for 2021-12-22 may include measurements
            from sleep that started on 2021-12-21.
        """
        return self._make_request(f"br/date/{date}.json", user_id=user_id)

    def get_breathing_rate_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Get breathing rate data for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format or 'today'
            end_date: End date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user

        Note:
            Maximum date range is 30 days.
            Data is collected during each day's main sleep period (longest sleep period).
            The measurement may reflect sleep that began the previous day.
        """
        return self._make_request(f"br/date/{start_date}/{end_date}.json", user_id=user_id)
