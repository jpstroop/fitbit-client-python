# resources/activity_timeseries.py
# Standard library imports
from typing import Any
from typing import Dict

# Local imports
from resources.base import BaseResource
from resources.constants import ActivityTimeSeriesPath
from resources.constants import Period


class ActivityTimeSeriesResource(BaseResource):
    """
    Handles Fitbit Activity Time Series API endpoints.
    API Reference: https://dev.fitbit.com/build/reference/web-api/activity-timeseries/
    """

    def get_time_series(
        self, resource_path: ActivityTimeSeriesPath, date: str, period: Period, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Get activity time series data for a period starting from the specified date.

        Parameters:
            resource_path: The resource path from ActivityTimeSeriesPath enum
            date: The end date in YYYY-MM-DD format or "today"
            period: Time period to get data for
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.
        """
        return self._make_request(
            f"activities/{resource_path.value}/date/{date}/{period.value}.json", user_id=user_id
        )

    def get_time_series_by_date_range(
        self,
        resource_path: ActivityTimeSeriesPath,
        start_date: str,
        end_date: str,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Get activity time series data for a specified date range.

        Parameters:
            resource_path: The resource path from ActivityTimeSeriesPath enum
            start_date: The start date in YYYY-MM-DD format or "today"
            end_date: The end date in YYYY-MM-DD format or "today"
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.

        Note:
            Maximum date ranges vary by resource type:
            - activityCalories: 30 days
            - Most other resources: 1095 days (~3 years)
        """
        return self._make_request(
            f"activities/{resource_path.value}/date/{start_date}/{end_date}.json", user_id=user_id
        )
