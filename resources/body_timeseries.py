# resources/body_timeseries.py
# Standard library imports
from typing import Any
from typing import Dict

# Local imports
from resources.base import BaseResource
from resources.constants import BodyResourceType
from resources.constants import BodyTimePeriod


class BodyTimeSeriesResource(BaseResource):
    """
    Handles Fitbit Body Time Series API endpoints for retrieving body measurements over time.

    API Reference: https://dev.fitbit.com/build/reference/web-api/body-timeseries/
    """

    def get_time_series_by_date(
        self, resource_type: BodyResourceType, date: str, period: BodyTimePeriod, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Get body metrics for a given resource over a period of time by specifying a date and time period.

        Args:
            resource_type: Type of body measurement (bmi, fat, or weight)
            date: The end date of the period in YYYY-MM-DD format or 'today'
            period: The range for which data will be returned
            user_id: Optional user ID, defaults to current user

        Note:
            For fat and weight resources, only periods up to 1m are supported - 3m, 6m, 1y, max are not available.
        """
        return self._make_request(
            f"body/{resource_type.value}/date/{date}/{period.value}.json", user_id=user_id
        )

    def get_time_series_by_date_range(
        self, resource_type: BodyResourceType, base_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Get body metrics for a given resource over a period of time by specifying a date range.

        Args:
            resource_type: Type of body measurement (bmi, fat, or weight)
            base_date: The start date in YYYY-MM-DD format or 'today'
            end_date: The end date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user

        Note:
            Maximum date ranges vary by resource:
            - bmi: 1095 days
            - fat: 30 days
            - weight: 31 days
        """
        return self._make_request(
            f"body/{resource_type.value}/date/{base_date}/{end_date}.json", user_id=user_id
        )

    def get_body_fat_time_series_by_date(
        self, date: str, period: BodyTimePeriod, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Get user's body fat measurements over a period of time by specifying a date and time period.

        Args:
            date: The end date in YYYY-MM-DD format or 'today'
            period: The range for which data will be returned (only up to 1m supported)
            user_id: Optional user ID, defaults to current user

        Note:
            Only periods up to 1m are supported - 3m, 6m, 1y, max are not available.
        """
        return self._make_request(f"body/log/fat/date/{date}/{period.value}.json", user_id=user_id)

    def get_body_fat_time_series_by_date_range(
        self, base_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Get user's body fat measurements over a period of time by specifying a date range.

        Args:
            base_date: The start date in YYYY-MM-DD format or 'today'
            end_date: The end date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user

        Note:
            Maximum range is 30 days
        """
        return self._make_request(f"body/log/fat/date/{base_date}/{end_date}.json", user_id=user_id)

    def get_weight_time_series_by_date(
        self, date: str, period: BodyTimePeriod, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Get user's weight measurements over a period of time by specifying a date and time period.

        Args:
            date: The end date in YYYY-MM-DD format or 'today'
            period: The range for which data will be returned (only up to 1m supported)
            user_id: Optional user ID, defaults to current user

        Note:
            Only periods up to 1m are supported - 3m, 6m, 1y, max are not available.
        """
        return self._make_request(
            f"body/log/weight/date/{date}/{period.value}.json", user_id=user_id
        )

    def get_weight_time_series_by_date_range(
        self, base_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Get user's weight measurements over a period of time by specifying a date range.

        Args:
            base_date: The start date in YYYY-MM-DD format or 'today'
            end_date: The end date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user

        Note:
            Maximum range is 31 days
        """
        return self._make_request(
            f"body/log/weight/date/{base_date}/{end_date}.json", user_id=user_id
        )
