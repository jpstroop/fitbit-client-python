# fitbit_client/resources/body_timeseries.py

# Standard library imports
from datetime import datetime
from typing import Any
from typing import Dict

# Local imports
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import BodyResourceType
from fitbit_client.resources.constants import BodyTimePeriod


class BodyTimeSeriesResource(BaseResource):
    """
    Handles Fitbit Body Time Series API endpoints for retrieving body measurements over time.

    API Reference: https://dev.fitbit.com/build/reference/web-api/body-timeseries/
    """

    MAX_DAYS = {
        BodyResourceType.BMI: 1095,  # ~3 years
        BodyResourceType.FAT: 30,
        BodyResourceType.WEIGHT: 31,
    }

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

        Returns:
            Body measurements for the specified period

        Raises:
            ValidationException: If date format is invalid

        Note:
            For fat and weight resources, only periods up to 1m are supported - 3m, 6m, 1y, max are not available.
        """
        try:
            if date != "today":
                datetime.strptime(date, "%Y-%m-%d")
        except ValueError as e:
            raise ValidationException(
                message=f"Invalid date format: {str(e)}",
                status_code=400,
                error_type="validation",
                field_name="date",
            )

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

        Returns:
            Body measurements for the specified date range

        Raises:
            ValidationException: If date format is invalid or date range exceeds maximum allowed days

        Note:
            Maximum date ranges vary by resource:
            - bmi: 1095 days
            - fat: 30 days
            - weight: 31 days
        """
        try:
            if base_date != "today":
                start = datetime.strptime(base_date, "%Y-%m-%d")
            if end_date != "today":
                end = datetime.strptime(end_date, "%Y-%m-%d")

            if base_date != "today" and end_date != "today":
                date_diff = (end - start).days
                max_days = self.MAX_DAYS[resource_type]
                if date_diff > max_days:
                    raise ValidationException(
                        message=f"Maximum date range for {resource_type.value} is {max_days} days",
                        status_code=400,
                        error_type="validation",
                        field_name="date_range",
                    )
        except ValueError as e:
            raise ValidationException(
                message=f"Invalid date format: {str(e)}",
                status_code=400,
                error_type="validation",
                field_name="date",
            )

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

        Returns:
            Body fat measurements for the specified period

        Raises:
            ValidationException: If date format is invalid

        Note:
            Only periods up to 1m are supported - 3m, 6m, 1y, max are not available.
        """
        return self.get_time_series_by_date(BodyResourceType.FAT, date, period, user_id)

    def get_body_fat_time_series_by_date_range(
        self, base_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Get user's body fat measurements over a period of time by specifying a date range.

        Args:
            base_date: The start date in YYYY-MM-DD format or 'today'
            end_date: The end date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user

        Returns:
            Body fat measurements for the specified date range

        Raises:
            ValidationException: If date format is invalid or date range exceeds 30 days

        Note:
            Maximum range is 30 days
        """
        return self.get_time_series_by_date_range(
            BodyResourceType.FAT, base_date, end_date, user_id
        )

    def get_weight_time_series_by_date(
        self, date: str, period: BodyTimePeriod, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Get user's weight measurements over a period of time by specifying a date and time period.

        Args:
            date: The end date in YYYY-MM-DD format or 'today'
            period: The range for which data will be returned (only up to 1m supported)
            user_id: Optional user ID, defaults to current user

        Returns:
            Weight measurements for the specified period

        Raises:
            ValidationException: If date format is invalid

        Note:
            Only periods up to 1m are supported - 3m, 6m, 1y, max are not available.
        """
        return self.get_time_series_by_date(BodyResourceType.WEIGHT, date, period, user_id)

    def get_weight_time_series_by_date_range(
        self, base_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Get user's weight measurements over a period of time by specifying a date range.

        Args:
            base_date: The start date in YYYY-MM-DD format or 'today'
            end_date: The end date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user

        Returns:
            Weight measurements for the specified date range

        Raises:
            ValidationException: If date format is invalid or date range exceeds 31 days

        Note:
            Maximum range is 31 days
        """
        return self.get_time_series_by_date_range(
            BodyResourceType.WEIGHT, base_date, end_date, user_id
        )
