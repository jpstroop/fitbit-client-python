# fitbit_client/resources/nutrition_timeseries.py

# Standard library imports
from enum import Enum
from typing import Any
from typing import Dict

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import NutritionResource
from fitbit_client.resources.constants import Period


class NutritionTimeSeriesResource(BaseResource):
    """
    Handles Fitbit Nutrition Time Series API endpoints for retrieving historical food and water data.

    API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition-timeseries/

    This resource provides access to daily summaries of:
    - Calorie consumption
    - Water consumption
    """

    def get_time_series_by_date(
        self, resource: NutritionResource, date: str, period: Period, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Retrieves nutrition data for a period starting from a specified date.

        Args:
            resource: Resource to query (CALORIES_IN or WATER)
            date: The end date in yyyy-MM-dd format or 'today'
            period: Time period for data (1d, 7d, 30d, 1w, 1m, 3m, 6m, 1y)
            user_id: Optional user ID, defaults to current user

        Returns:
            Dictionary containing daily summary values for the specified period

        Note:
            Returns data using units corresponding to Accept-Language header.
            Only returns data since user's join date or first log entry.
        """
        return self._make_request(
            f"foods/log/{resource.value}/date/{date}/{period.value}.json", user_id=user_id
        )

    def get_time_series_by_date_range(
        self, resource: NutritionResource, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Retrieves nutrition data for a specified date range.

        Args:
            resource: Resource to query (CALORIES_IN or WATER)
            start_date: Start date in yyyy-MM-dd format or 'today'
            end_date: End date in yyyy-MM-dd format or 'today'
            user_id: Optional user ID, defaults to current user

        Returns:
            Dictionary containing daily summary values for the date range

        Note:
            Maximum range is 1095 days (~3 years).
            Returns data using units corresponding to Accept-Language header.
            Only returns data since user's join date or first log entry.
        """
        return self._make_request(
            f"foods/log/{resource.value}/date/{start_date}/{end_date}.json", user_id=user_id
        )
