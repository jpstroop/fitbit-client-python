# fitbit_client/resources/active_zone_minutes.py

# Standard library imports
from typing import cast

# Local imports
from fitbit_client.exceptions import IntradayValidationException
from fitbit_client.resources._base import BaseResource
from fitbit_client.resources._constants import Period
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params
from fitbit_client.utils.types import JSONDict


class ActiveZoneMinutesResource(BaseResource):
    """Provides access to Fitbit Active Zone Minutes (AZM) API for heart rate-based activity metrics.

    This resource handles endpoints for retrieving Active Zone Minutes (AZM) data, which measures
    the time users spend in target heart rate zones during exercise or daily activities. AZM
    is a scientifically-validated way to track activity intensity based on personalized heart
    rate zones rather than just steps.

    Different zones contribute differently to the total AZM count:
    - Fat Burn zone: 1 minute = 1 AZM (moderate intensity)
    - Cardio zone: 1 minute = 2 AZM (high intensity)
    - Peak zone: 1 minute = 2 AZM (maximum effort)

    API Reference: https://dev.fitbit.com/build/reference/web-api/active-zone-minutes-timeseries/

    Required Scopes:
        - activity (for all AZM endpoints)

    Note:
        - Heart rate zones are personalized based on the user's resting heart rate and age
        - The American Heart Association recommends 150 minutes of moderate (Fat Burn) or
          75 minutes of vigorous (Cardio/Peak) activity per week
        - AZM data is available from the date the user first set up their Fitbit device
        - Historical data older than 3 years may not be available through the API
        - Not all Fitbit devices support AZM tracking (requires heart rate monitoring)
        - The date range endpoints are useful for analyzing weekly and monthly AZM totals
    """

    @validate_date_param()
    def get_azm_timeseries_by_date(
        self, date: str, period: Period = Period.ONE_DAY, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Returns Active Zone Minutes time series data for a period ending on the specified date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/active-zone-minutes-timeseries/get-azm-timeseries-by-date/

        Args:
            date: The end date of the period in YYYY-MM-DD format or 'today'
            period: The range for which data will be returned. Only Period.ONE_DAY (1d) is supported.
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Daily Active Zone Minutes data

        Raises:
            fitbit_client.exceptions.IntradayValidationException: If period is not Period.ONE_DAY
            fitbit_client.exceptions.InvalidDateException: If date format is invalid

        Note:
            - Only Period.ONE_DAY (1d) is currently supported by the Fitbit API
            - activeZoneMinutes is the sum total of all zone minutes with cardio and peak
              minutes counting double (fatBurn + (cardio × 2) + (peak × 2))
            - Fat burn zone is typically 50-69% of max heart rate (moderate intensity)
            - Cardio zone is typically 70-84% of max heart rate (high intensity)
            - Peak zone is typically 85%+ of max heart rate (maximum effort)
            - Days with no AZM data will show all metrics as zero
        """
        if period != Period.ONE_DAY:
            raise IntradayValidationException(
                message="Only 1d period is supported for AZM time series",
                field_name="period",
                allowed_values=[Period.ONE_DAY.value],
                resource_name="active zone minutes",
            )

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
        """Returns Active Zone Minutes time series data for a specified date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/active-zone-minutes-timeseries/get-azm-timeseries-by-interval/

        Args:
            start_date: The start date in YYYY-MM-DD format or 'today'
            end_date: The end date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Daily Active Zone Minutes data for each date in the range

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.InvalidDateRangeException: If date range is invalid or exceeds 1095 days

        Note:
            - Maximum date range is 1095 days (approximately 3 years)
            - Each day's entry includes separate counts for each heart rate zone
            - activeZoneMinutes is the total AZM with cardio and peak minutes counting double
            - This endpoint is useful for calculating weekly or monthly AZM totals
            - Days with no AZM data will have all metrics as zero
            - Active Zone Minutes does not support subscription notifications (webhooks),
              but can be queried after activity notifications arrive
            - Weekly AZM goals can be tracked by summing 7 consecutive days of data
        """
        result = self._make_request(
            f"activities/active-zone-minutes/date/{start_date}/{end_date}.json",
            user_id=user_id,
            debug=debug,
        )
        return cast(JSONDict, result)
