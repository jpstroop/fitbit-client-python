# fitbit_client/resources/active_zone_minutes.py

# Standard library imports
from typing import Any
from typing import Dict
from typing import cast

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import Period
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params
from fitbit_client.utils.types import JSONDict


class ActiveZoneMinutesResource(BaseResource):
    """
    Handles Fitbit Active Zone Minutes (AZM) API endpoints for retrieving user's
    heart-pumping activity data throughout the day.

    Active Zone Minutes (AZM) measure the time spent in target heart rate zones.
    Different zones contribute differently to the total AZM count:
    - Fat Burn zone: 1 minute = 1 AZM
    - Cardio zone: 1 minute = 2 AZM
    - Peak zone: 1 minute = 2 AZM

    API Reference: https://dev.fitbit.com/build/reference/web-api/active-zone-minutes-timeseries/
    """

    @validate_date_param()
    def get_azm_timeseries_by_date(
        self, date: str, period: Period = Period.ONE_DAY, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """
        Get Active Zone Minutes time series data for a period starting from the specified date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/active-zone-minutes-timeseries/get-azm-timeseries-by-date/

        Args:
            date: The end date of the period in yyyy-MM-dd format or 'today'
            period: The range for which data will be returned. Only Period.ONE_DAY (1d) is supported.
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Daily AZM data including:
            - activeZoneMinutes: Total count of active zone minutes
            - fatBurnActiveZoneMinutes: Minutes in fat burn zone (1 minute = 1 AZM)
            - cardioActiveZoneMinutes: Minutes in cardio zone (1 minute = 2 AZM)
            - peakActiveZoneMinutes: Minutes in peak zone (1 minute = 2 AZM)

        Raises:
            ValueError: If period is not Period.ONE_DAY
            InvalidDateException: If date format is invalid
        """
        if period != Period.ONE_DAY:
            raise ValueError("Only 1d period is supported for AZM time series")

        result = self._make_request(
            f"activities/active-zone-minutes/date/{date}/{period.value}.json",
            user_id=user_id,
            debug=debug,
        )
        return cast(JSONDict, result)

    @validate_date_range_params(max_days=1095, resource_name="AZM time series")
    def get_azm_timeseries_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """
        Get Active Zone Minutes time series data for a specified date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/active-zone-minutes-timeseries/get-azm-timeseries-by-interval/

        Args:
            start_date: The start date in yyyy-MM-dd format or 'today'
            end_date: The end date in yyyy-MM-dd format or 'today'
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Daily AZM data for each date in the range including:
            - activeZoneMinutes: Total count of active zone minutes
            - fatBurnActiveZoneMinutes: Minutes in fat burn zone (1 minute = 1 AZM)
            - cardioActiveZoneMinutes: Minutes in cardio zone (1 minute = 2 AZM)
            - peakActiveZoneMinutes: Minutes in peak zone (1 minute = 2 AZM)

        Raises:
            InvalidDateException: If date format is invalid
            InvalidDateRangeException: If date range is invalid or exceeds 1095 days

        Note:
            Maximum date range is 1095 days (approximately 3 years)
        """
        result = self._make_request(
            f"activities/active-zone-minutes/date/{start_date}/{end_date}.json",
            user_id=user_id,
            debug=debug,
        )
        return cast(JSONDict, result)
