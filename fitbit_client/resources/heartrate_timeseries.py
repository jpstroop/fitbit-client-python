# fitbit_client/resources/heartrate_timeseries.py

# Standard library imports
from typing import Optional
from typing import cast

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import Period
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params
from fitbit_client.utils.types import JSONDict


class HeartrateTimeSeriesResource(BaseResource):
    """
    Handles Fitbit Heart Rate Time Series API endpoints for retrieving time-series heart rate data.

    API Reference: https://dev.fitbit.com/build/reference/web-api/heartrate-timeseries/

    Note:
        This resource requires the 'heartrate' scope.
        Data is limited to the user's join date or first log entry date.
        Responses include daily summary values including heart rate zones and resting heart rate.
        For intraday resolution, see the IntradayResource class.
    """

    @validate_date_param(field_name="date")
    def get_heartrate_timeseries_by_date(
        self,
        date: str,
        period: Period,
        user_id: str = "-",
        timezone: Optional[str] = None,
        debug: bool = False,
    ) -> JSONDict:
        """
        Retrieves heart rate time series data for a period starting from the specified date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/heartrate-timeseries/get-heartrate-timeseries-by-date/

        Args:
            date: The end date in yyyy-MM-dd format or 'today'
            period: Time period to retrieve data for.
                   Supported values: 1d, 7d, 30d, 1w, 1m
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.
            timezone: Optional timezone (only 'UTC' supported)
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Heart rate data including:
            - Date/time of measurement
            - Custom heart rate zones with calories, ranges, and minutes
            - Standard heart rate zones (Out of Range, Fat Burn, Cardio, Peak)
            - Resting heart rate if available

        Raises:
            ValueError: If period is not supported
            ValueError: If timezone is not 'UTC'
            InvalidDateException: If date format is invalid

        Note:
            Resting heart rate is calculated from measurements throughout the day,
            prioritizing sleep periods. If insufficient data exists for a day,
            resting heart rate may not be available.
        """
        supported_periods = {
            Period.ONE_DAY,
            Period.SEVEN_DAYS,
            Period.THIRTY_DAYS,
            Period.ONE_WEEK,
            Period.ONE_MONTH,
        }

        if period not in supported_periods:
            raise ValueError(
                f"Period must be one of: {', '.join(p.value for p in supported_periods)}"
            )

        if timezone is not None and timezone != "UTC":
            raise ValueError("Only 'UTC' timezone is supported")

        params = {"timezone": timezone} if timezone else None
        result = self._make_request(
            f"activities/heart/date/{date}/{period.value}.json",
            params=params,
            user_id=user_id,
            debug=debug,
        )
        return cast(JSONDict, result)

    @validate_date_range_params()
    def get_heartrate_timeseries_by_date_range(
        self,
        start_date: str,
        end_date: str,
        user_id: str = "-",
        timezone: Optional[str] = None,
        debug: bool = False,
    ) -> JSONDict:
        """
        Retrieves heart rate time series data for a specified date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/heartrate-timeseries/get-heartrate-timeseries-by-date-range/

        Args:
            start_date: Start date in yyyy-MM-dd format or 'today'
            end_date: End date in yyyy-MM-dd format or 'today'
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.
            timezone: Optional timezone (only 'UTC' supported)
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Heart rate data including:
            - Date/time of measurement
            - Custom heart rate zones with calories, ranges, and minutes
            - Standard heart rate zones (Out of Range, Fat Burn, Cardio, Peak)
            - Resting heart rate if available

        Raises:
            ValueError: If timezone is not 'UTC'
            InvalidDateException: If date format is invalid
            InvalidDateRangeException: If start_date is after end_date

        Note:
            Maximum date range is 1 year.
            Resting heart rate is calculated from measurements throughout the day,
            prioritizing sleep periods. If insufficient data exists for a day,
            resting heart rate may not be available.
        """
        if timezone is not None and timezone != "UTC":
            raise ValueError("Only 'UTC' timezone is supported")

        params = {"timezone": timezone} if timezone else None
        result = self._make_request(
            f"activities/heart/date/{start_date}/{end_date}.json",
            params=params,
            user_id=user_id,
            debug=debug,
        )
        return cast(JSONDict, result)
