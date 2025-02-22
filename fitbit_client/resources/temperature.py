# fitbit_client/resources/temperature.py

# Standard library imports
from typing import Any
from typing import Dict

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params


class TemperatureResource(BaseResource):
    """
    Handles Fitbit Temperature API endpoints for retrieving both manually logged
    core temperature data and automatically measured skin temperature data.

    Core temperature data is manually logged by users, while skin temperature is
    measured during sleep periods using either dedicated temperature sensors or
    other device sensors.

    API Reference: https://dev.fitbit.com/build/reference/web-api/temperature/
    """

    @validate_date_param(field_name="date")
    def get_temperature_core_summary_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Get core temperature summary data for a single date. Temperature
        (Core) data applies specifically to data logged manually by the user throughout
        the day.

        API Reference: https://dev.fitbit.com/build/reference/web-api/temperature/get-temperature-core-summary-by-date

        Args:
            date: Date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Core temperature measurements manually logged by the user for the date.
            Values are in Celsius or Fahrenheit based on Accept-Language header.

        Raises:
            InvalidDateException: If date format is invalid
        """
        return self._make_request(f"temp/core/date/{date}.json", user_id=user_id, debug=debug)

    @validate_date_range_params(max_days=30)
    def get_temperature_core_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Get core temperature data for a date range. Temperature (Core) data applies
        specifically to data logged manually by the user on a given day. Maximum date
        range cannot exceed 30 days.

        API Reference: https://dev.fitbit.com/build/reference/web-api/temperature/get-temperature-core-summary-by-interval

        Args:
            start_date: Start date in YYYY-MM-DD format or "today"
            end_date: End date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Core temperature measurements for each date in the range. Values use units
            that correspond to the Accept-Language header provided.

        Raises:
            InvalidDateException: If date format is invalid
            InvalidDateRangeException: If start_date is after end_date or date range exceeds 30 days

        Note:
            Maximum date range is 30 days
        """
        return self._make_request(
            f"temp/core/date/{start_date}/{end_date}.json", user_id=user_id, debug=debug
        )

    @validate_date_param(field_name="date")
    def get_temperature_skin_summary_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Get skin temperature data for a single date. Temperature (Skin) data applies
        specifically to a user's "main sleep," which is the longest single period of time
        asleep on a given date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/temperature/get-temperature-skin-summary-by-date

        Args:
            date: Date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Skin temperature measurements from the user's main sleep period. Values are relative
            to baseline temperature in Celsius or Fahrenheit based on Accept-Language header.

        Raises:
            InvalidDateException: If date format is invalid

        Note:
            - Requires at least 3 hours of quality sleep
            - Data typically spans two dates since it's measured during overnight sleep
            - Takes ~15 minutes after device sync for data to be available
            - Requires minimal movement during sleep for accurate measurements
            - The data returned usually reflects a sleep period that began the day before
        """
        return self._make_request(f"temp/skin/date/{date}.json", user_id=user_id, debug=debug)

    @validate_date_range_params(max_days=30)
    def get_temperature_skin_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Get skin temperature data for a date range. It only returns a value for dates
        on which the Fitbit device was able to record Temperature (skin) data and the
        maximum date range cannot exceed 30 days.

        API Reference: https://dev.fitbit.com/build/reference/web-api/temperature/get-temperature-skin-summary-by-interval

        Args:
            start_date: Start date in YYYY-MM-DD format or "today"
            end_date: End date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Skin temperature measurements for the main sleep period of each date.
            Only includes dates where valid measurements were taken. Values use units
            that correspond to the Accept-Language header provided.

        Raises:
            InvalidDateException: If date format is invalid
            InvalidDateRangeException: If start_date is after end_date or date range exceeds 30 days

        Note:
            - Maximum date range is 30 days
            - Data typically spans two dates since it's measured during overnight sleep
            - Requires at least 3 hours of quality sleep
            - Takes ~15 minutes after device sync for data to be available
            - The data returned usually reflects sleep periods that began the day before
        """
        return self._make_request(
            f"temp/skin/date/{start_date}/{end_date}.json", user_id=user_id, debug=debug
        )
