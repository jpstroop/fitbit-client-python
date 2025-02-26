# fitbit_client/resources/heartrate_variability.py

# Standard library imports
from typing import cast

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params
from fitbit_client.utils.types import JSONDict


class HeartrateVariabilityResource(BaseResource):
    """
    Handles Fitbit Heart Rate Variability (HRV) API endpoints for retrieving daily and interval HRV data.

    API Reference: https://dev.fitbit.com/build/reference/web-api/heartrate-variability/

    Note:
        This resource requires the 'heartrate' scope.
        HRV data is collected only during the user's "main sleep" (longest sleep period) and requires:
        - Enabled Health Metrics tile in mobile app dashboard
        - Minimum 3 hours of sleep
        - Creation of sleep stages log during main sleep period
        - Device compatibility (check Fitbit Product page for supported devices)

        Data processing occurs after device sync and takes ~15 minutes to become available.
        HRV measurements span sleep periods that may begin on the previous day.
        Premium subscription is not required for HRV data collection.
    """

    @validate_date_param(field_name="date")
    def get_hrv_summary_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """
        Retrieves HRV summary data for a single date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/heartrate-variability/get-hrv-summary-by-date/

        Args:
            date: Date in yyyy-MM-dd format or 'today'
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            HRV data including:
            - dateTime: Sleep log date
            - value:
                - dailyRmssd: Daily heart rate variability (RMSSD) in milliseconds
                - deepRmssd: Deep sleep heart rate variability (RMSSD) in milliseconds

        Raises:
            InvalidDateException: If date format is invalid

        Note:
            Data reflects the main sleep period, which may have started the previous day.
            A 200 status code indicates successful execution, even if no data exists.
            For reliable data collection, users should remain still during sleep measurement.
        """
        result = self._make_request(f"hrv/date/{date}.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    @validate_date_range_params()
    def get_hrv_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """
        Retrieves HRV summary data for a date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/heartrate-variability/get-hrv-summary-by-interval/

        Args:
            start_date: Start date in yyyy-MM-dd format or 'today'
            end_date: End date in yyyy-MM-dd format or 'today'
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            HRV data for each date including:
            - dateTime: Sleep log date
            - value:
                - dailyRmssd: Daily heart rate variability (RMSSD) in milliseconds
                - deepRmssd: Deep sleep heart rate variability (RMSSD) in milliseconds

        Raises:
            InvalidDateException: If date format is invalid
            InvalidDateRangeException: If start_date is after end_date

        Note:
            Maximum date range is 30 days.
            Data reflects main sleep periods, which may have started the day before each date.
            A 200 status code indicates successful execution, even if no data exists.
            Since HRV data requires sleep, consider querying once or twice daily (e.g., noon and midnight).
        """
        result = self._make_request(
            f"hrv/date/{start_date}/{end_date}.json", user_id=user_id, debug=debug
        )
        return cast(JSONDict, result)
