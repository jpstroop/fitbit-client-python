# fitbit_client/resources/temperature.py

# Standard library imports
from typing import cast

# Local imports
from fitbit_client.resources._base import BaseResource
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params
from fitbit_client.utils.types import JSONDict


class TemperatureResource(BaseResource):
    """Provides access to Fitbit Temperature API for retrieving temperature measurements.

    This resource handles endpoints for retrieving two types of temperature data:
    1. Core temperature: Manually logged by users (e.g., using a thermometer)
    2. Skin temperature: Automatically measured during sleep by compatible Fitbit devices

    The API provides methods to retrieve data for single dates or date ranges.
    Temperature data is useful for tracking fever, monitoring menstrual cycles,
    and identifying potential health changes.

    API Reference: https://dev.fitbit.com/build/reference/web-api/temperature/

    Required Scopes:
        - temperature (for all temperature endpoints)

    Note:
        - Core temperature is in absolute values (e.g., 37.0°C)
        - Skin temperature is reported as variation from baseline (e.g., +0.5°C)
        - Temperature units (Celsius vs Fahrenheit) are determined by the Accept-Language header
        - Not all Fitbit devices support skin temperature measurements
        - Skin temperature measurements require at least 3 hours of quality sleep
    """

    @validate_date_param(field_name="date")
    def get_temperature_core_summary_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Returns core temperature summary data for a single date.

        This endpoint retrieves temperature data that was manually logged by the user
        on the specified date, typically using a thermometer.

        API Reference: https://dev.fitbit.com/build/reference/web-api/temperature/get-temperature-core-summary-by-date

        Args:
            date: Date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Core temperature measurements containing date, time and temperature values

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid

        Note:
            - Temperature values are in Celsius or Fahrenheit based on the Accept-Language header
            - Core temperature is the body's internal temperature, not skin temperature
            - Normal core temperature range is typically 36.5°C to 37.5°C (97.7°F to 99.5°F)
            - If no temperature was logged for the date, an empty array is returned
        """
        result = self._make_request(f"temp/core/date/{date}.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    @validate_date_range_params(max_days=30)
    def get_temperature_core_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Returns core temperature data for a specified date range.

        This endpoint retrieves temperature data that was manually logged by the user
        across the specified date range, typically using a thermometer.

        API Reference: https://dev.fitbit.com/build/reference/web-api/temperature/get-temperature-core-summary-by-interval

        Args:
            start_date: Start date in YYYY-MM-DD format or "today"
            end_date: End date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Core temperature measurements for each date in the range with time and temperature values

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.InvalidDateRangeException: If start_date is after end_date or
                date range exceeds 30 days

        Note:
            - Maximum date range is 30 days
            - Temperature values are in Celsius or Fahrenheit based on the Accept-Language header
            - Days with no logged temperature data will not appear in the results
            - Multiple temperature entries on the same day will all be included
            - The datetime field includes the specific time the measurement was logged
        """
        result = self._make_request(
            f"temp/core/date/{start_date}/{end_date}.json", user_id=user_id, debug=debug
        )
        return cast(JSONDict, result)

    @validate_date_param(field_name="date")
    def get_temperature_skin_summary_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Returns skin temperature data for a single date.

        This endpoint retrieves skin temperature data that was automatically measured during
        the user's main sleep period (longest sleep) on the specified date. Skin temperature
        is reported as variation from the user's baseline, not absolute temperature.

        API Reference: https://dev.fitbit.com/build/reference/web-api/temperature/get-temperature-skin-summary-by-date

        Args:
            date: Date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Skin temperature measurements containing date and nightly relative values

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid

        Note:
            - Requires compatible Fitbit device with skin temperature measurement capability
            - Values are relative to the user's baseline (e.g., +0.5°C, -0.2°C)
            - Requires at least 3 hours of quality sleep for measurement
            - Data typically spans two dates since it's measured during overnight sleep
            - Takes ~15 minutes after device sync for data to be available
            - The data returned usually reflects a sleep period that began the day before
            - Significant temperature variations may indicate illness, menstrual cycle changes,
              or changes in sleeping environment
        """
        result = self._make_request(f"temp/skin/date/{date}.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    @validate_date_range_params(max_days=30)
    def get_temperature_skin_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Returns skin temperature data for a specified date range.

        This endpoint retrieves skin temperature data that was automatically measured during
        the user's main sleep periods across the specified date range. It only returns values
        for dates when the Fitbit device successfully recorded skin temperature data.

        API Reference: https://dev.fitbit.com/build/reference/web-api/temperature/get-temperature-skin-summary-by-interval

        Args:
            start_date: Start date in YYYY-MM-DD format or "today"
            end_date: End date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Skin temperature measurements for each date in the range with nightly relative values

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.InvalidDateRangeException: If start_date is after end_date or
                date range exceeds 30 days

        Note:
            - Maximum date range is 30 days
            - Values are relative to the user's baseline (e.g., +0.5°C, -0.2°C)
            - Days without valid measurements will not appear in the results
            - Data typically spans two dates since it's measured during overnight sleep
            - The "nightlyRelative" value shows how the measured temperature differs from
              the user's baseline, which is calculated from approximately 30 days of data
            - Tracking trends over time can be more informative than individual readings
        """
        result = self._make_request(
            f"temp/skin/date/{start_date}/{end_date}.json", user_id=user_id, debug=debug
        )
        return cast(JSONDict, result)
