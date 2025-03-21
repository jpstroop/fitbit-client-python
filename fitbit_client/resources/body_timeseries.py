# fitbit_client/resources/body_timeseries.py

# Standard library imports
from typing import cast

# Local imports
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources._base import BaseResource
from fitbit_client.resources._constants import BodyResourceType
from fitbit_client.resources._constants import BodyTimePeriod
from fitbit_client.resources._constants import MaxRanges
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range
from fitbit_client.utils.date_validation import validate_date_range_params
from fitbit_client.utils.types import JSONDict


class BodyTimeSeriesResource(BaseResource):
    """Provides access to Fitbit Body Time Series API for retrieving body measurements over time.

    This resource handles endpoints for retrieving historical body measurement data
    including weight, body fat percentage, and BMI over specified time periods.
    It enables tracking and analysis of body composition changes over time.

    API Reference: https://dev.fitbit.com/build/reference/web-api/body-timeseries/

    Required Scopes:
      - weight: Required for all endpoints in this resource

    Note:
        The Body Time Series API provides access to historical body measurement data,
        which is useful for tracking trends and progress over time. Each measurement
        type (weight, body fat, BMI) has specific date range limitations:

        - BMI data: Available for up to 1095 days (3 years)
        - Body fat data: Available for up to 30 days
        - Weight data: Available for up to 31 days

        Measurements are returned in the user's preferred unit system (metric or imperial),
        which can be determined by the Accept-Language header provided during API calls.

        Data is recorded when users log body measurements manually or when they use
        connected scales that automatically sync with their Fitbit account.
    """

    @validate_date_param()
    def get_body_timeseries_by_date(
        self,
        resource_type: BodyResourceType,
        date: str,
        period: BodyTimePeriod,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """Retrieves body metrics for a given resource over a period ending on the specified date.

        This endpoint returns time series data for the specified body measurement type
        (BMI, body fat percentage, or weight) over a time period ending on the given date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body-timeseries/get-body-timeseries-by-date/

        Args:
            resource_type: Type of body measurement (BodyResourceType.BMI, BodyResourceType.FAT,
                          or BodyResourceType.WEIGHT)
            date: The end date in YYYY-MM-DD format or 'today'
            period: The time period for data retrieval (e.g., BodyTimePeriod.ONE_DAY,
                   BodyTimePeriod.SEVEN_DAYS, etc.)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Time series data for the specified body measurement type and time period

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.ValidationException: If period is not supported for fat/weight
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            For fat and weight resources, only periods up to BodyTimePeriod.ONE_MONTH are supported.
            The periods BodyTimePeriod.THREE_MONTHS, BodyTimePeriod.SIX_MONTHS,
            BodyTimePeriod.ONE_YEAR, and BodyTimePeriod.MAX are not available for these resources.

            The JSON field name in the response varies based on resource_type:
            - BodyResourceType.BMI: "body-bmi"
            - BodyResourceType.FAT: "body-fat"
            - BodyResourceType.WEIGHT: "body-weight"

            Values are returned as strings representing:
            - Weight: kilograms or pounds based on user settings
            - Body fat: percentage (e.g., "22.5" means 22.5%)
            - BMI: standard BMI value (e.g., "21.3")

            The endpoint returns all available data points within the requested period,
            which may include multiple measurements per day if the user logged them.
            Days without measurements will not appear in the results.
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

        result = self._make_request(
            f"body/{resource_type.value}/date/{date}/{period.value}.json",
            user_id=user_id,
            debug=debug,
        )
        return cast(JSONDict, result)

    @validate_date_range_params(start_field="begin_date")
    def get_body_timeseries_by_date_range(
        self,
        resource_type: BodyResourceType,
        begin_date: str,
        end_date: str,
        user_id: str = "-",
        debug: bool = False,
    ) -> (
        JSONDict
    ):  # Note: This is the one place in the whole API where it's called "begin_date" not "start_date" ¯\_(ツ)_/¯
        """Retrieves body metrics for a given resource over a specified date range.

        This endpoint returns time series data for the specified body measurement type
        (BMI, body fat percentage, or weight) between two specified dates.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body-timeseries/get-body-timeseries-by-date-range/

        Args:
            resource_type: Type of body measurement (BodyResourceType.BMI, BodyResourceType.FAT,
                          or BodyResourceType.WEIGHT)
            begin_date: The start date in YYYY-MM-DD format or 'today'
            end_date: The end date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Time series data for the specified body measurement type and date range

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.InvalidDateRangeException: If date range exceeds maximum allowed days
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Maximum date ranges vary by resource type:
            - BMI: 1095 days (3 years)
            - FAT: 30 days
            - WEIGHT: 31 days

            The JSON field name in the response varies based on resource_type:
            - BodyResourceType.BMI: "body-bmi"
            - BodyResourceType.FAT: "body-fat"
            - BodyResourceType.WEIGHT: "body-weight"

            Values are returned as strings representing:
            - Weight: kilograms or pounds based on user settings
            - Body fat: percentage (e.g., "22.5" means 22.5%)
            - BMI: standard BMI value (e.g., "21.3")

            The endpoint returns all available data points within the requested date range,
            which may include multiple measurements per day if the user logged them.
            Days without measurements will not appear in the results.

            Uniquely in the Fitbit API, this endpoint uses "begin_date" rather than
            "start_date" in its URL path (unlike most other Fitbit API endpoints).
        """
        max_days = {
            BodyResourceType.BMI: MaxRanges.GENERAL,
            BodyResourceType.FAT: MaxRanges.BODY_FAT,
            BodyResourceType.WEIGHT: MaxRanges.WEIGHT,
        }[resource_type]

        # Since we have different max days for different resources, we need to validate here
        validate_date_range(begin_date, end_date, max_days, resource_type.value)

        result = self._make_request(
            f"body/{resource_type.value}/date/{begin_date}/{end_date}.json",
            user_id=user_id,
            debug=debug,
        )
        return cast(JSONDict, result)

    @validate_date_param()
    def get_bodyfat_timeseries_by_date(
        self, date: str, period: BodyTimePeriod, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Returns body fat percentage data for a specified time period.

        This endpoint retrieves time series data for body fat percentage measurements
        over a period ending on the specified date. This provides a convenient way
        to track changes in body composition over time.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body-timeseries/get-bodyfat-timeseries-by-date/

        Args:
            date: The end date in YYYY-MM-DD format or 'today'
            period: The range for which data will be returned (only up to 1m supported)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Body fat percentage time series data for the specified time period

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.ValidationException: If period is not supported

        Note:
            Only periods up to BodyTimePeriod.ONE_MONTH are supported. The periods
            BodyTimePeriod.THREE_MONTHS, BodyTimePeriod.SIX_MONTHS, BodyTimePeriod.ONE_YEAR,
            and BodyTimePeriod.MAX are not available for body fat data.

            The endpoint will return all available data points within the requested period,
            which may include multiple measurements per day if the user logged them.
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

        result = self._make_request(
            f"body/log/fat/date/{date}/{period.value}.json", user_id=user_id, debug=debug
        )
        return cast(JSONDict, result)

    @validate_date_range_params(max_days=MaxRanges.BODY_FAT, resource_name="body fat")
    def get_bodyfat_timeseries_by_date_range(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Retrieves body fat percentage measurements over a specified date range.

        This endpoint returns all body fat percentage logs between the specified start and end dates.
        Body fat percentage is a key metric for tracking body composition changes over time.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body-timeseries/get-bodyfat-timeseries-by-date-range/

        Args:
            start_date: The start date in YYYY-MM-DD format or 'today'
            end_date: The end date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Body fat percentage time series data for the specified date range

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.InvalidDateRangeException: If date range exceeds 30 days
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Maximum range is 30 days for body fat percentage data. Requests for longer
            periods will result in an InvalidDateRangeException.

            Body fat percentage values are returned as strings representing percentages
            (e.g., "22.5" means 22.5% body fat).

            The endpoint returns all available data points within the requested range,
            which may include multiple measurements per day if the user logged them.
            Days without measurements will not appear in the results.
        """
        result = self._make_request(
            f"body/log/fat/date/{start_date}/{end_date}.json", user_id=user_id, debug=debug
        )
        return cast(JSONDict, result)

    @validate_date_param()
    def get_weight_timeseries_by_date(
        self, date: str, period: BodyTimePeriod, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Retrieves weight measurements over a period ending on the specified date.

        This endpoint returns weight logs over a time period ending on the specified date.
        Weight data is presented in the user's preferred unit system (kilograms or pounds).

        API Reference: https://dev.fitbit.com/build/reference/web-api/body-timeseries/get-weight-timeseries-by-date/

        Args:
            date: The end date in YYYY-MM-DD format or 'today'
            period: The range for which data will be returned (only up to ONE_MONTH supported)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Weight time series data for the specified time period

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.ValidationException: If period is not supported
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Only periods up to BodyTimePeriod.ONE_MONTH are supported. The periods
            BodyTimePeriod.THREE_MONTHS, BodyTimePeriod.SIX_MONTHS, BodyTimePeriod.ONE_YEAR,
            and BodyTimePeriod.MAX are not available for weight data.

            Weight values are returned as strings representing either:
            - Kilograms for users with metric settings
            - Pounds for users with imperial settings

            The unit system is determined by the user's account settings and
            can also be influenced by the Accept-Language header provided
            during API calls.
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

        result = self._make_request(
            f"body/log/weight/date/{date}/{period.value}.json", user_id=user_id, debug=debug
        )
        return cast(JSONDict, result)

    @validate_date_range_params(max_days=MaxRanges.WEIGHT, resource_name="weight")
    def get_weight_timeseries_by_date_range(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Retrieves weight measurements over a specified date range.

        This endpoint returns all weight logs between the specified start and end dates.
        Weight data is presented in the user's preferred unit system (kilograms or pounds).

        API Reference: https://dev.fitbit.com/build/reference/web-api/body-timeseries/get-weight-timeseries-by-date-range/

        Args:
            start_date: The start date in YYYY-MM-DD format or 'today'
            end_date: The end date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Weight time series data for the specified date range

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.InvalidDateRangeException: If date range exceeds 31 days
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Maximum range is 31 days for weight data. Requests for longer periods
            will result in an InvalidDateRangeException.

            Weight values are returned as strings representing either:
            - Kilograms for users with metric settings
            - Pounds for users with imperial settings

            The endpoint returns all available data points within the requested range,
            which may include multiple measurements per day if the user logged them.
            Days without measurements will not appear in the results.

            To retrieve weight data for longer historical periods, you can make multiple
            requests with different date ranges and combine the results.
        """
        result = self._make_request(
            f"body/log/weight/date/{start_date}/{end_date}.json", user_id=user_id, debug=debug
        )
        return cast(JSONDict, result)
