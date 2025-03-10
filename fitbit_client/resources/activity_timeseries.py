# fitbit_client/resources/activity_timeseries.py

# Standard library imports
from typing import cast

# Local imports
from fitbit_client.resources._base import BaseResource
from fitbit_client.resources._constants import ActivityTimeSeriesPath
from fitbit_client.resources._constants import Period
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params
from fitbit_client.utils.types import JSONDict


class ActivityTimeSeriesResource(BaseResource):
    """Provides access to Fitbit Activity Time Series API for retrieving historical activity data.

    This resource handles endpoints for retrieving time series data for various activity metrics
    such as steps, distance, calories, active minutes, and floors over specified time periods.
    Time series data is useful for analyzing trends, creating visualizations, and tracking
    progress over time.

    API Reference: https://dev.fitbit.com/build/reference/web-api/activity-timeseries/

    Required Scopes:
        - activity (for all activity time series endpoints)

    Note:
        - Time series data is available from the date the user created their Fitbit account
        - Data is organized by date with one data point per day
        - Various activity metrics are available including steps, distance, floors, calories, etc.
        - Historical data can be accessed either by period (e.g., 1d, 7d, 30d) or date range
        - Maximum date ranges vary by resource type (most allow ~3 years of historical data)
        - For more granular intraday data, see the Intraday resource
    """

    @validate_date_param()
    def get_activity_timeseries_by_date(
        self,
        resource_path: ActivityTimeSeriesPath,
        date: str,
        period: Period,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """Returns activity time series data for a period ending on the specified date.

        This endpoint provides historical activity data for a specific time period (e.g., 1d, 7d, 30d)
        ending on the specified date. It's useful for retrieving recent activity history with a
        consistent timeframe.

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity-timeseries-by-date/

        Args:
            resource_path: The resource path from ActivityTimeSeriesPath enum (e.g.,
                          ActivityTimeSeriesPath.STEPS, ActivityTimeSeriesPath.DISTANCE)
            date: The end date in YYYY-MM-DD format or "today"
            period: Time period to get data for (e.g., Period.ONE_DAY, Period.SEVEN_DAYS, Period.THIRTY_DAYS)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Activity time series data for the specified activity metric and time period

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.InvalidRequestException: If resource_path or period is invalid

        Note:
            - The response format varies slightly depending on the resource_path
            - All values are returned as strings and need to be converted to appropriate types
            - For numeric resources like steps, values should be converted to integers
            - The number of data points equals the number of days in the period
            - Data is returned in ascending date order (oldest first)
            - If no data exists for a particular day, the value may be "0" or the day may be omitted
            - Period options include 1d, 7d, 30d, 1w, 1m, 3m, 6m, 1y
        """
        result = self._make_request(
            f"activities/{resource_path.value}/date/{date}/{period.value}.json",
            user_id=user_id,
            debug=debug,
        )
        return cast(JSONDict, result)

    @validate_date_range_params(max_days=1095, resource_name="activity time series")
    def get_activity_timeseries_by_date_range(
        self,
        resource_path: ActivityTimeSeriesPath,
        start_date: str,
        end_date: str,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """Returns activity time series data for a specified date range.

        This endpoint provides historical activity data for a custom date range between two
        specified dates. It's useful for analyzing activity patterns over specific time periods
        or generating custom reports.

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity-timeseries-by-date-range/

        Args:
            resource_path: The resource path from ActivityTimeSeriesPath enum (e.g.,
                          ActivityTimeSeriesPath.STEPS, ActivityTimeSeriesPath.CALORIES)
            start_date: The start date in YYYY-MM-DD format or "today"
            end_date: The end date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Activity time series data for the specified activity metric and date range

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.InvalidDateRangeException: If date range is invalid or exceeds maximum allowed days
            fitbit_client.exceptions.InvalidRequestException: If resource_path is invalid

        Note:
            - Maximum date ranges vary by resource type:
              * ActivityTimeSeriesPath.ACTIVITY_CALORIES: 30 days maximum
              * Most other resources: 1095 days (~3 years) maximum
            - The response format varies slightly depending on the resource_path
            - All values are returned as strings and need to be converted to appropriate types
            - Data is returned in ascending date order (oldest first)
            - The date range is inclusive of both start_date and end_date
            - For longer date ranges, consider making multiple requests with smaller ranges
            - If no data exists for a particular day, the value may be "0" or the day may be omitted
        """
        result = self._make_request(
            f"activities/{resource_path.value}/date/{start_date}/{end_date}.json",
            user_id=user_id,
            debug=debug,
        )
        return cast(JSONDict, result)
