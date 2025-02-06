# fitbit_client/resources/activity_timeseries.py

# Standard library imports
from typing import Any
from typing import Dict

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import ActivityTimeSeriesPath
from fitbit_client.resources.constants import Period
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params


class ActivityTimeSeriesResource(BaseResource):
    """
    Handles Fitbit Activity Time Series API endpoints.

    API Reference: https://dev.fitbit.com/build/reference/web-api/activity-timeseries/
    """

    @validate_date_param()
    def get_activity_timeseries_by_date(
        self,
        resource_path: ActivityTimeSeriesPath,
        date: str,
        period: Period,
        user_id: str = "-",
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Get activity time series data for a period starting from the specified date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity-timeseries-by-date/

        Parameters:
            resource_path: The resource path from ActivityTimeSeriesPath enum
            date: The end date in YYYY-MM-DD format or "today"
            period: Time period to get data for
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Raises:
            InvalidDateException: If date format is invalid
        """
        return self._make_request(
            f"activities/{resource_path.value}/date/{date}/{period.value}.json",
            user_id=user_id,
            debug=debug,
        )

    @validate_date_range_params(max_days=1095, resource_name="activity time series")
    def get_activity_timeseries_by_date_range(
        self,
        resource_path: ActivityTimeSeriesPath,
        start_date: str,
        end_date: str,
        user_id: str = "-",
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Get activity time series data for a specified date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity-timeseries-by-date-range/

        Parameters:
            resource_path: The resource path from ActivityTimeSeriesPath enum
            start_date: The start date in YYYY-MM-DD format or "today"
            end_date: The end date in YYYY-MM-DD format or "today"
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Raises:
            InvalidDateException: If date format is invalid
            InvalidDateRangeException: If date range is invalid or exceeds maximum allowed days

        Note:
            Maximum date ranges vary by resource type:
            - activityCalories: 30 days
            - Most other resources: 1095 days (~3 years)
        """
        return self._make_request(
            f"activities/{resource_path.value}/date/{start_date}/{end_date}.json",
            user_id=user_id,
            debug=debug,
        )
