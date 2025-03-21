# fitbit_client/resources/breathing_rate.py

# Standard library imports
from typing import cast

# Local imports
from fitbit_client.resources._base import BaseResource
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params
from fitbit_client.utils.types import JSONDict


class BreathingRateResource(BaseResource):
    """Provides access to Fitbit Breathing Rate API for retrieving respiratory measurements.

    This resource handles endpoints for retrieving breathing rate (respiratory rate) data,
    which measures the average breaths per minute during sleep. The API provides both daily
    summaries and interval-based historical data.

    API Reference: https://dev.fitbit.com/build/reference/web-api/breathing-rate/

    Required Scopes: respiratory_rate

    Note:
        Data is collected during the user's "main sleep" period (longest sleep period) and
        requires specific conditions:
        - Sleep periods must be at least 3 hours long
        - User must be relatively still during measurement
        - Data becomes available approximately 15 minutes after device sync
        - Sleep periods may span across midnight, so data might reflect previous day's sleep
        - Not all Fitbit devices support breathing rate measurement
    """

    @validate_date_param()
    def get_breathing_rate_summary_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Returns breathing rate data summary for a single date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/breathing-rate/get-br-summary-by-date/

        Args:
            date: Date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Breathing rate data containing average breaths per minute during sleep

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid

        Note:
            Data is collected during the user's main sleep period (longest sleep period).
            The measurement may reflect sleep that began the previous day.
            For example, requesting data for 2023-01-01 may include measurements
            from sleep that started on 2022-12-31.

            Not all fields may be present in the response, depending on the
            Fitbit device model and quality of sleep data captured.

            Breathing rate data requires:
            - Compatible Fitbit device that supports this measurement
            - Sleep period at least 3 hours long
            - Relatively still sleep (excessive movement reduces accuracy)
        """
        result = self._make_request(f"br/date/{date}.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    @validate_date_range_params(max_days=30)
    def get_breathing_rate_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Returns breathing rate data for a specified date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/breathing-rate/get-br-summary-by-interval/

        Args:
            start_date: Start date in YYYY-MM-DD format or 'today'
            end_date: End date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Breathing rate data for each day in the specified date range

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.InvalidDateRangeException: If date range exceeds 30 days
                or start_date is after end_date

        Note:
            Maximum date range is 30 days.
            Data for each day is collected during that day's main sleep period (longest sleep).
            Measurements may reflect sleep that began on the previous day.

            Days without valid breathing rate data (insufficient sleep, device not worn, etc.)
            will not appear in the results array.

            Breathing rate values are typically in the range of 12-20 breaths per minute during
            sleep, with deep sleep typically showing slightly lower rates than REM sleep.
            The 'lowBreathingRateDisturbances' field counts instances where the breathing rate
            dropped significantly below the user's normal range during sleep.
        """
        result = self._make_request(
            f"br/date/{start_date}/{end_date}.json", user_id=user_id, debug=debug
        )
        return cast(JSONDict, result)
