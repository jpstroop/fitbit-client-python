# fitbit_client/resources/nutrition_timeseries.py

# Standard library imports
from typing import cast

# Local imports
from fitbit_client.resources._base import BaseResource
from fitbit_client.resources._constants import NutritionResource
from fitbit_client.resources._constants import Period
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params
from fitbit_client.utils.types import JSONDict


class NutritionTimeSeriesResource(BaseResource):
    """Provides access to Fitbit Nutrition Time Series API for retrieving historical nutrition data.

    This resource handles endpoints for retrieving historical food and water consumption data
    over time. It provides daily summaries of calorie and water intake, allowing applications
    to display trends and patterns in nutritional data over various time periods.

    API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition-timeseries/

    Required Scopes:
      - nutrition: Required for all endpoints in this resource

    Note:
        This resource provides access to daily summaries of:
        - Calorie consumption (caloriesIn)
        - Water consumption (water)

        The data is always returned with date values and can be queried either by
        specifying a base date and period, or by providing explicit start and end dates.

        All water measurements are returned in the unit system specified by the Accept-Language
        header provided during client initialization (fluid ounces for en_US, milliliters
        for most other locales).
    """

    @validate_date_param(field_name="date")
    def get_nutrition_timeseries_by_date(
        self,
        resource: NutritionResource,
        date: str,
        period: Period,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """Returns nutrition data for a period ending on the specified date.

        This endpoint retrieves daily summaries of calorie intake or water consumption
        for a specified time period ending on the given date. It provides historical
        nutrition data that can be used to analyze trends over time.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition-timeseries/get-nutrition-timeseries-by-date/

        Args:
            resource: Resource to query (NutritionResource.CALORIES_IN or NutritionResource.WATER)
            date: The end date in YYYY-MM-DD format or 'today'
            period: Time period for data (e.g., Period.ONE_DAY, Period.ONE_WEEK, Period.ONE_MONTH)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Dictionary containing daily summary values for calorie intake or water consumption,
                  with dates and corresponding values for each day in the period

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Data is returned in chronological order (oldest first). The API only returns
            data from the user's join date or first log entry onward. Days with no logged
            data may be omitted from the response.

            Water values are returned in the unit system specified by the Accept-Language
            header (fluid ounces for en_US, milliliters for most other locales).
        """
        result = self._make_request(
            f"foods/log/{resource.value}/date/{date}/{period.value}.json",
            user_id=user_id,
            debug=debug,
        )
        return cast(JSONDict, result)

    @validate_date_range_params(max_days=1095)
    def get_nutrition_timeseries_by_date_range(
        self,
        resource: NutritionResource,
        start_date: str,
        end_date: str,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """Returns nutrition data for a specified date range.

        This endpoint retrieves daily summaries of calorie intake or water consumption
        for a specific date range. It allows for more precise control over the time
        period compared to the period-based endpoint.

        API Reference: https://dev.fitbit.com/build/reference/web-api/nutrition-timeseries/get-nutrition-timeseries-by-date-range/

        Args:
            resource: Resource to query (NutritionResource.CALORIES_IN or NutritionResource.WATER)
            start_date: Start date in YYYY-MM-DD format or 'today'
            end_date: End date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Dictionary containing daily summary values for calorie intake or water consumption,
                  with dates and corresponding values for each day in the specified date range

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.InvalidDateRangeException: If start_date is after end_date
                or date range exceeds 1095 days
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Maximum date range is 1095 days (approximately 3 years).

            Data is returned in chronological order (oldest first). The API only returns
            data from the user's join date or first log entry onward. Days with no logged
            data may be omitted from the response.

            Water values are returned in the unit system specified by the Accept-Language
            header (fluid ounces for en_US, milliliters for most other locales).

            This endpoint returns the same data format as get_nutrition_timeseries_by_date,
            but allows for more precise control over the date range.
        """
        result = self._make_request(
            f"foods/log/{resource.value}/date/{start_date}/{end_date}.json",
            user_id=user_id,
            debug=debug,
        )
        return cast(JSONDict, result)
