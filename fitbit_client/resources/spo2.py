# fitbit_client/resources/spo2.py

# Standard library imports
from typing import Any
from typing import Dict

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params


class SpO2Resource(BaseResource):
    """
    Handles Fitbit SpO2 (Blood Oxygen Saturation) API endpoints for retrieving
    oxygen saturation measurements taken during sleep.

    The data represents measurements taken during the user's "main sleep" period
    (longest sleep period) and typically spans two dates since measurements are
    taken during overnight sleep.

    API Reference: https://dev.fitbit.com/build/reference/web-api/spo2/
    """

    @validate_date_param(field_name="date")
    def get_spo2_summary_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Get SpO2 summary data for a specific date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/spo2/get-spo2-summary-by-date/

        Args:
            date: Date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            SpO2 summary including average, minimum and maximum levels for the date.
            Note that data typically reflects sleep that began the previous day.

        Raises:
            InvalidDateException: If date format is invalid

        Note:
            SpO2 data requires:
            - At least 3 hours of quality sleep
            - Minimal movement during sleep
            - Device sync after waking
            - Up to 1 hour processing time after sync
        """
        return self._make_request(f"spo2/date/{date}.json", user_id=user_id, debug=debug)

    @validate_date_range_params()
    def get_spo2_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Get SpO2 summary data for a date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/spo2/get-spo2-summary-by-interval/

        Args:
            start_date: Start date in YYYY-MM-DD format or "today"
            end_date: End date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            List of daily SpO2 summaries including average, minimum and maximum
            levels for each date in the range.

        Raises:
            InvalidDateException: If date format is invalid
            InvalidDateRangeException: If start_date is after end_date

        Note:
            Unlike many other endpoints, there is no maximum date range limit
            for this endpoint.
        """
        return self._make_request(
            f"spo2/date/{start_date}/{end_date}.json", user_id=user_id, debug=debug
        )
