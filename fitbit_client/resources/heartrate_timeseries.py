# fitbit_client/resources/heartrate_timeseries.py

# Standard library imports
from typing import Optional
from typing import cast

# Local imports
from fitbit_client.exceptions import IntradayValidationException
from fitbit_client.exceptions import ParameterValidationException
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import Period
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params
from fitbit_client.utils.types import JSONDict


class HeartrateTimeSeriesResource(BaseResource):
    """Provides access to Fitbit Heart Rate Time Series API for retrieving heart rate data.

    This resource handles endpoints for retrieving daily heart rate summaries including
    heart rate zones, resting heart rate, and time spent in each zone. It provides data
    for specific dates or date ranges.

    API Reference: https://dev.fitbit.com/build/reference/web-api/heartrate-timeseries/

    Required Scopes: heartrate

    Note:
        Data availability is limited to the user's join date or first log entry date.
        Responses include daily summary values but not minute-by-minute data.
        For intraday (minute-level) heart rate data, use the IntradayResource class.
        This resource requires a heart rate capable Fitbit device.
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
        """Returns heart rate time series data for a period ending on the specified date.

        This endpoint retrieves daily heart rate summaries for a specified time period ending
        on the given date. The data includes resting heart rate and time spent in different
        heart rate zones for each day in the period.

        API Reference: https://dev.fitbit.com/build/reference/web-api/heartrate-timeseries/get-heartrate-timeseries-by-date/

        Args:
            date: The end date in YYYY-MM-DD format or 'today'
            period: Time period to retrieve data for (must be one of: Period.ONE_DAY,
                   Period.SEVEN_DAYS, Period.THIRTY_DAYS, Period.ONE_WEEK, Period.ONE_MONTH)
            user_id: Optional user ID, defaults to current user ("-")
            timezone: Optional timezone (only 'UTC' supported)
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Heart rate data for each day in the period, including heart rate zones and resting heart rate

        Raises:
            fitbit_client.exceptions.IntradayValidationException: If period is not one of the supported period values
            fitbit_client.exceptions.ParameterValidationException: If timezone is provided and not 'UTC'
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.AuthorizationException: If the required scope is not granted

        Note:
            Resting heart rate is calculated from measurements throughout the day,
            prioritizing sleep periods. If insufficient data exists for a day,
            the restingHeartRate field may be missing from that day's data.

            Each heart rate zone contains:
            - name: Zone name (Out of Range, Fat Burn, Cardio, Peak)
            - min/max: The heart rate boundaries for this zone in beats per minute
            - minutes: Total time spent in this zone in minutes
            - caloriesOut: Estimated calories burned while in this zone

            The standard zones are calculated based on the user's profile data (age, gender, etc.)
            and represent different exercise intensities:
            - Out of Range: Below 50% of max heart rate
            - Fat Burn: 50-69% of max heart rate
            - Cardio: 70-84% of max heart rate
            - Peak: 85-100% of max heart rate
        """
        supported_periods = {
            Period.ONE_DAY,
            Period.SEVEN_DAYS,
            Period.THIRTY_DAYS,
            Period.ONE_WEEK,
            Period.ONE_MONTH,
        }

        if period not in supported_periods:
            raise IntradayValidationException(
                message=f"Period must be one of the supported values",
                field_name="period",
                allowed_values=[p.value for p in supported_periods],
                resource_name="heart rate",
            )

        if timezone is not None and timezone != "UTC":
            raise ParameterValidationException(
                message="Only 'UTC' timezone is supported", field_name="timezone"
            )

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
        """Returns heart rate time series data for a specified date range.

        This endpoint retrieves daily heart rate summaries for each day in the specified date range.
        The data includes resting heart rate and time spent in different heart rate zones for each
        day in the range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/heartrate-timeseries/get-heartrate-timeseries-by-date-range/

        Args:
            start_date: Start date in YYYY-MM-DD format or 'today'
            end_date: End date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user ("-")
            timezone: Optional timezone (only 'UTC' supported)
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Heart rate data for each day in the date range, including heart rate zones and resting heart rate

        Raises:
            fitbit_client.exceptions.ParameterValidationException: If timezone is provided and not 'UTC'
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.InvalidDateRangeException: If start_date is after end_date or
                if the date range exceeds the maximum allowed (1095 days)
            fitbit_client.exceptions.AuthorizationException: If the required scope is not granted

        Note:
            Maximum date range is 1095 days (approximately 3 years).

            Resting heart rate is calculated from measurements throughout the day,
            prioritizing sleep periods. If insufficient data exists for a particular day,
            the restingHeartRate field may be missing from that day's data.

            Each heart rate zone contains:
            - name: Zone name (Out of Range, Fat Burn, Cardio, Peak)
            - min/max: The heart rate boundaries for this zone in beats per minute
            - minutes: Total time spent in this zone in minutes
            - caloriesOut: Estimated calories burned while in this zone

            This endpoint returns the same data format as the get_heartrate_timeseries_by_date
            method, but allows for more precise control over the date range.
        """
        if timezone is not None and timezone != "UTC":
            raise ParameterValidationException(
                message="Only 'UTC' timezone is supported", field_name="timezone"
            )

        params = {"timezone": timezone} if timezone else None
        result = self._make_request(
            f"activities/heart/date/{start_date}/{end_date}.json",
            params=params,
            user_id=user_id,
            debug=debug,
        )
        return cast(JSONDict, result)
