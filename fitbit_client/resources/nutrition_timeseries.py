# fitbit_client/resources/nutrition_timeseries.py

# Standard library imports
from typing import Any
from typing import Dict

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import NutritionResource
from fitbit_client.resources.constants import Period
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params


class NutritionTimeSeriesResource(BaseResource):
    """
    Handles Fitbit Nutrition Time Series API endpoints for retrieving historical food and water data.

    API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition-timeseries/

    This resource provides access to daily summaries of:
    - Calorie consumption
    - Water consumption
    """

    @validate_date_param(field_name="date")
    def get_nutrition_timeseries_by_date(
        self,
        resource: NutritionResource,
        date: str,
        period: Period,
        user_id: str = "-",
        debug=False,
    ) -> Dict[str, Any]:
        """
        Retrieves nutrition data for a period starting from a specified date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition-timeseries/get-nutrition-timeseries-by-date/

        Args:
            resource: Resource to query (CALORIES_IN or WATER)
            date: The end date in yyyy-MM-dd format or 'today'
            period: Time period for data (1d, 7d, 30d, 1w, 1m, 3m, 6m, 1y)
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Dictionary containing daily summary values for the specified period

        Raises:
            InvalidDateException: If date format is invalid

        Note:
            Returns data using units corresponding to Accept-Language header.
            Only returns data since user's join date or first log entry.
        """
        return self._make_request(
            f"foods/log/{resource.value}/date/{date}/{period.value}.json",
            user_id=user_id,
            debug=debug,
        )

    @validate_date_range_params(max_days=1095)
    def get_nutrition_timeseries_by_date_range(
        self,
        resource: NutritionResource,
        start_date: str,
        end_date: str,
        user_id: str = "-",
        debug=False,
    ) -> Dict[str, Any]:
        """
        Retrieves nutrition data for a specified date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition-timeseries/get-nutrition-timeseries-by-date-range/

        Args:
            resource: Resource to query (CALORIES_IN or WATER)
            start_date: Start date in yyyy-MM-dd format or 'today'
            end_date: End date in yyyy-MM-dd format or 'today'
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Dictionary containing daily summary values for the date range

        Raises:
            InvalidDateException: If date format is invalid
            InvalidDateRangeException: If start_date is after end_date or date range exceeds 1095 days

        Note:
            Maximum range is 1095 days (~3 years).
            Returns data using units corresponding to Accept-Language header.
            Only returns data since user's join date or first log entry.
        """
        return self._make_request(
            f"foods/log/{resource.value}/date/{start_date}/{end_date}.json",
            user_id=user_id,
            debug=debug,
        )
