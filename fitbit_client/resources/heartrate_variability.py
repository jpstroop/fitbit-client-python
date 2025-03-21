# fitbit_client/resources/heartrate_variability.py

# Standard library imports
from typing import cast

# Local imports
from fitbit_client.resources._base import BaseResource
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params
from fitbit_client.utils.types import JSONDict


class HeartrateVariabilityResource(BaseResource):
    """Provides access to Fitbit Heart Rate Variability (HRV) API for retrieving daily metrics.

    This resource handles endpoints for retrieving HRV measurements taken during sleep, which
    is a key indicator of recovery, stress, and overall autonomic nervous system health.

    API Reference: https://dev.fitbit.com/build/reference/web-api/heartrate-variability/

    Required Scopes:
      - heartrate: Required for all endpoints in this resource

    Note:
        Heart Rate Variability (HRV) measures the variation in time between consecutive
        heartbeats. High HRV generally indicates better cardiovascular fitness, stress
        resilience, and recovery capacity. Low HRV may indicate stress, fatigue, or illness.

        HRV is calculated using the RMSSD (Root Mean Square of Successive Differences)
        measurement in milliseconds. Typical healthy adult values range from 20-100ms,
        with higher values generally indicating better autonomic function.

        HRV data collection requirements:
        - Enabled Health Metrics tile in mobile app dashboard
        - Minimum 3 hours of sleep
        - Creation of sleep stages log during main sleep period
        - Device compatibility (check Fitbit Product page for supported devices)
        - No Premium subscription required

        Data processing occurs after device sync and takes ~15 minutes to become available.
        HRV measurements span sleep periods that may begin on the previous day.
    """

    @validate_date_param(field_name="date")
    def get_hrv_summary_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Retrieves HRV summary data for a single date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/heartrate-variability/get-hrv-summary-by-date/

        Args:
            date: Date in YYYY-MM-DD format or 'today'
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: HRV data containing daily and deep sleep RMSSD measurements for the requested date

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Data reflects the main sleep period, which may have started the previous day.
            The response may be empty if no HRV data was collected for the requested date.

            Two RMSSD values are provided:
            - dailyRmssd: Calculated across all sleep stages during the main sleep session
            - deepRmssd: Calculated only during deep sleep, which typically shows lower
              HRV values due to increased parasympathetic nervous system dominance

            For reliable data collection, users should wear their device properly and
            remain still during sleep measurement. Environmental factors like alcohol,
            caffeine, or stress can affect HRV measurements.
        """
        result = self._make_request(f"hrv/date/{date}.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    @validate_date_range_params()
    def get_hrv_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Retrieves HRV summary data for a date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/heartrate-variability/get-hrv-summary-by-interval/

        Args:
            start_date: Start date in YYYY-MM-DD format or 'today'
            end_date: End date in YYYY-MM-DD format or 'today'
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: HRV data containing daily and deep sleep RMSSD measurements for multiple dates in the requested range

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.InvalidDateRangeException: If start_date is after end_date
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Maximum date range is 30 days. Requests exceeding this limit will return an error.

            The response includes entries only for dates where HRV data was collected.
            Dates without data will not appear in the results array.

            HRV data is calculated from sleep sessions, which may have started on the
            previous day. The dateTime field represents the date the sleep session
            ended, not when it began.

            Tracking HRV over time provides insights into:
            - Recovery status and adaptation to training
            - Potential early warning signs of overtraining or illness
            - Effects of lifestyle changes on autonomic nervous system function

            For optimal trend analysis, collect data consistently at the same time each day.
        """
        result = self._make_request(
            f"hrv/date/{start_date}/{end_date}.json", user_id=user_id, debug=debug
        )
        return cast(JSONDict, result)
