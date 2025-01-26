# Standard library imports
from typing import Any
from typing import Dict

# Local imports
from fitbit_client.resources.base import BaseResource


class TemperatureResource(BaseResource):
    """
    Handles Fitbit Temperature API endpoints for retrieving both manually logged
    core temperature data and automatically measured skin temperature data.

    Core temperature data is manually logged by users, while skin temperature is
    measured during sleep periods using either dedicated temperature sensors or
    other device sensors.

    API Reference: https://dev.fitbit.com/build/reference/web-api/temperature/
    """

    def get_core_summary_by_date(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Get core temperature summary data for a specific date.

        Args:
            date: Date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user

        Returns:
            Core temperature measurements manually logged by the user for the date.
            Values are in Celsius or Fahrenheit based on Accept-Language header.
        """
        return self._make_request(f"temp/core/date/{date}.json", user_id=user_id)

    def get_core_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Get core temperature summary data for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format or "today"
            end_date: End date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user

        Returns:
            Core temperature measurements for each date in the range

        Note:
            Maximum date range is 30 days
        """
        return self._make_request(f"temp/core/date/{start_date}/{end_date}.json", user_id=user_id)

    def get_skin_summary_by_date(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Get skin temperature summary data for a specific date.

        Args:
            date: Date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user

        Returns:
            Skin temperature measurements from the user's main sleep period.
            Values are relative to baseline temperature in Celsius or Fahrenheit.

        Note:
            - Requires at least 3 hours of quality sleep
            - Data typically spans two dates since it's measured during overnight sleep
            - Takes ~15 minutes after device sync for data to be available
            - Requires minimal movement during sleep for accurate measurements
        """
        return self._make_request(f"temp/skin/date/{date}.json", user_id=user_id)

    def get_skin_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Get skin temperature summary data for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format or "today"
            end_date: End date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user

        Returns:
            Skin temperature measurements for the main sleep period of each date.
            Only includes dates where valid measurements were taken.

        Note:
            - Maximum date range is 30 days
            - Data typically spans two dates since it's measured during overnight sleep
            - Requires at least 3 hours of quality sleep
            - Takes ~15 minutes after device sync for data to be available
        """
        return self._make_request(f"temp/skin/date/{start_date}/{end_date}.json", user_id=user_id)
