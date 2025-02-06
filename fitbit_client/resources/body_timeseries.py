# fitbit_client/resources/body_timeseries.py

# Standard library imports
from typing import Any
from typing import Dict

# Local imports
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import BodyResourceType
from fitbit_client.resources.constants import BodyTimePeriod
from fitbit_client.resources.constants import MaxRanges
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range
from fitbit_client.utils.date_validation import validate_date_range_params


class BodyTimeSeriesResource(BaseResource):
    """
    Handles Fitbit Body Time Series API endpoints for retrieving body measurements over time.

    API Reference: https://dev.fitbit.com/build/reference/web-api/body-timeseries/
    """

    @validate_date_param()
    def get_body_timeseries_by_date(
        self,
        resource_type: BodyResourceType,
        date: str,
        period: BodyTimePeriod,
        user_id: str = "-",
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Get body metrics for a given resource over a period of time by specifying a date and time period.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body-timeseries/get-body-timeseries-by-date/

        Args:
            resource_type: Type of body measurement (bmi, fat, or weight)
            date: The end date in YYYY-MM-DD format or 'today'
            period: The range for which data will be returned
            user_id: Optional user ID, defaults to current user
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Body measurements for the specified period

        Raises:
            InvalidDateException: If date format is invalid
            ValidationException: If period is not supported for fat/weight

        Note:
            For fat and weight resources, only periods up to 1m are supported - 3m, 6m, 1y, max are not available.
            Data is returned using units based on the Accept-Language header provided.
        """
        # Validate period restrictions for fat and weight
        if resource_type in (BodyResourceType.FAT, BodyResourceType.WEIGHT):
            if period in (
                BodyTimePeriod.THREE_MONTHS,
                BodyTimePeriod.SIX_MONTHS,
                BodyTimePeriod.ONE_YEAR,
                BodyTimePeriod.MAX,
            ):
                raise ValidationException(
                    message=f"Period {period.value} not supported for {resource_type.value}",
                    status_code=400,
                    error_type="validation",
                    field_name="period",
                )

        return self._make_request(
            f"body/{resource_type.value}/date/{date}/{period.value}.json",
            user_id=user_id,
            debug=debug,
        )

    @validate_date_range_params()
    def get_body_timeseries_by_date_range(
        self,
        resource_type: BodyResourceType,
        start_date: str,
        end_date: str,
        user_id: str = "-",
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Get body metrics for a given resource over a period of time by specifying a date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body-timeseries/get-body-timeseries-by-date-range/

        Args:
            resource_type: Type of body measurement (bmi, fat, or weight)
            start_date: The start date in YYYY-MM-DD format or 'today'
            end_date: The end date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Body measurements for the specified date range

        Raises:
            InvalidDateException: If date format is invalid
            InvalidDateRangeException: If date range exceeds maximum allowed days

        Note:
            Maximum date ranges vary by resource:
            - bmi: 1095 days
            - fat: 30 days
            - weight: 31 days
            Data is returned using units based on the Accept-Language header provided.
        """
        max_days = {
            BodyResourceType.BMI: MaxRanges.GENERAL,
            BodyResourceType.FAT: MaxRanges.BODY_FAT,
            BodyResourceType.WEIGHT: MaxRanges.WEIGHT,
        }[resource_type]

        # Since we have different max days for different resources, we need to validate here
        validate_date_range(start_date, end_date, max_days, resource_type.value)

        return self._make_request(
            f"body/{resource_type.value}/date/{start_date}/{end_date}.json",
            user_id=user_id,
            debug=debug,
        )

    @validate_date_param()
    def get_bodyfat_timeseries_by_date(
        self, date: str, period: BodyTimePeriod, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Get user's body fat measurements over a period of time by specifying a date and time period.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body-timeseries/get-bodyfat-timeseries-by-date/

        Args:
            date: The end date in YYYY-MM-DD format or 'today'
            period: The range for which data will be returned (only up to 1m supported)
            user_id: Optional user ID, defaults to current user
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Body fat measurements for the specified period

        Raises:
            InvalidDateException: If date format is invalid
            ValidationException: If period is not supported

        Note:
            Only periods up to 1m are supported - 3m, 6m, 1y, max are not available.
            Data is returned using units based on the Accept-Language header provided.
        """
        if period in (
            BodyTimePeriod.THREE_MONTHS,
            BodyTimePeriod.SIX_MONTHS,
            BodyTimePeriod.ONE_YEAR,
            BodyTimePeriod.MAX,
        ):
            raise ValidationException(
                message=f"Period {period.value} not supported for body fat",
                status_code=400,
                error_type="validation",
                field_name="period",
            )

        return self._make_request(
            f"body/log/fat/date/{date}/{period.value}.json", user_id=user_id, debug=debug
        )

    @validate_date_range_params(max_days=MaxRanges.BODY_FAT, resource_name="body fat")
    def get_bodyfat_timeseries_by_date_range(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Get user's body fat measurements over a period of time by specifying a date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body-timeseries/get-bodyfat-timeseries-by-date-range/

        Args:
            start_date: The start date in YYYY-MM-DD format or 'today'
            end_date: The end date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Body fat measurements for the specified date range

        Raises:
            InvalidDateException: If date format is invalid
            InvalidDateRangeException: If date range exceeds 30 days

        Note:
            Maximum range is 30 days
            Data is returned using units based on the Accept-Language header provided.
        """
        return self._make_request(
            f"body/log/fat/date/{start_date}/{end_date}.json", user_id=user_id, debug=debug
        )

    @validate_date_param()
    def get_weight_timeseries_by_date(
        self, date: str, period: BodyTimePeriod, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Get user's weight measurements over a period of time by specifying a date and time period.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body-timeseries/get-weight-timeseries-by-date/

        Args:
            date: The end date in YYYY-MM-DD format or 'today'
            period: The range for which data will be returned (only up to 1m supported)
            user_id: Optional user ID, defaults to current user
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Weight measurements for the specified period

        Raises:
            InvalidDateException: If date format is invalid
            ValidationException: If period is not supported

        Note:
            Only periods up to 1m are supported - 3m, 6m, 1y, max are not available.
            Data is returned using units based on the Accept-Language header provided.
        """
        if period in (
            BodyTimePeriod.THREE_MONTHS,
            BodyTimePeriod.SIX_MONTHS,
            BodyTimePeriod.ONE_YEAR,
            BodyTimePeriod.MAX,
        ):
            raise ValidationException(
                message=f"Period {period.value} not supported for weight",
                status_code=400,
                error_type="validation",
                field_name="period",
            )

        return self._make_request(
            f"body/log/weight/date/{date}/{period.value}.json", user_id=user_id, debug=debug
        )

    @validate_date_range_params(max_days=MaxRanges.WEIGHT, resource_name="weight")
    def get_weight_timeseries_by_date_range(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Get user's weight measurements over a period of time by specifying a date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body-timeseries/get-weight-timeseries-by-date-range/

        Args:
            start_date: The start date in YYYY-MM-DD format or 'today'
            end_date: The end date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Weight measurements for the specified date range

        Raises:
            InvalidDateException: If date format is invalid
            InvalidDateRangeException: If date range exceeds 31 days

        Note:
            Maximum range is 31 days
            Data is returned using units based on the Accept-Language header provided.
        """
        return self._make_request(
            f"body/log/weight/date/{start_date}/{end_date}.json", user_id=user_id, debug=debug
        )
