# fitbit_client/resources/sleep.py

# Standard library imports
from typing import Any
from typing import Dict
from typing import Optional

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import SortDirection
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params
from fitbit_client.utils.pagination_validation import validate_pagination_params


class SleepResource(BaseResource):
    """
    Handles Fitbit Sleep API endpoints for recording, retrieving and managing
    user sleep data and goals.

    API Reference: https://dev.fitbit.com/build/reference/web-api/sleep/

    Note:
        All Sleep endpoints use API version 1.2
    """

    API_VERSION: str = "1.2"

    def create_sleep_goals(
        self, min_duration: int, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Creates or updates a user's sleep goal.

        API Reference: https://dev.fitbit.com/build/reference/web-api/sleep/create-sleep-goals/

        Args:
            min_duration: Length of sleep goal in minutes
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Sleep goal details including min duration and update timestamp
        """
        if min_duration <= 0:
            raise ValueError("min_duration must be positive")

        return self._make_request(
            "sleep/goal.json",
            data={"minDuration": min_duration},
            user_id=user_id,
            http_method="POST",
            api_version=SleepResource.API_VERSION,
            debug=debug,
        )

    create_sleep_goal = create_sleep_goals  # semantically correct name

    @validate_date_param(field_name="date")
    def create_sleep_log(
        self,
        date: str,
        duration_millis: int,
        start_time: str,
        user_id: str = "-",
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Creates a log entry for a sleep event.

        API Reference: https://dev.fitbit.com/build/reference/web-api/sleep/create-sleep-log/

        Args:
            date: Log date in YYYY-MM-DD format
            duration_millis: Duration in milliseconds
            start_time: Activity start time (HH:mm)
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Created sleep log entry details

        Raises:
            ValueError: If duration_millis is not positive
            InvalidDateException: If date format is invalid

        Note:
            - It is NOT possible to create overlapping log entries
            - The dateOfSleep in the response is the date on which the sleep event ends
            - Manual logs default to "classic" type since they lack the device
              heart rate and movement data needed for "stages" type
        """
        if duration_millis <= 0:
            raise ValueError("duration_millis must be positive")

        params = {"startTime": start_time, "duration": duration_millis, "date": date}
        return self._make_request(
            "sleep.json",
            params=params,
            user_id=user_id,
            http_method="POST",
            api_version=SleepResource.API_VERSION,
            debug=debug,
        )

    def delete_sleep_log(
        self, log_id: int, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Deletes a specific sleep log entry.

        API Reference: https://dev.fitbit.com/build/reference/web-api/sleep/delete-sleep-log/

        Args:
            log_id: ID of the sleep log to delete
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)
        """
        return self._make_request(
            f"sleep/{log_id}.json",
            user_id=user_id,
            http_method="DELETE",
            api_version=SleepResource.API_VERSION,
            debug=debug,
        )

    def get_sleep_goals(self, user_id: str = "-", debug: bool = False) -> Dict[str, Any]:
        """
        Gets a user's current sleep goal.

        API Reference: https://dev.fitbit.com/build/reference/web-api/sleep/get-sleep-goals/

        Args:
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Sleep goal details including:
            - minDuration: Length of sleep goal in minutes
            - consistency: Sleep goal consistency flow status
            - updatedOn: Last update timestamp
        """
        return self._make_request(
            "sleep/goal.json", user_id=user_id, api_version=SleepResource.API_VERSION, debug=debug
        )

    get_sleep_goal = get_sleep_goals  # semantically correct name

    @validate_date_param(field_name="date")
    def get_sleep_log_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Gets sleep logs for a specific date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/sleep/get-sleep-log-by-date/

        Args:
            date: The date in YYYY-MM-DD format
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Sleep logs and summary for the specified date including:
            - Classic logs: asleep, restless, awake levels (60-sec granularity)
            - Stages logs: deep, light, rem, wake levels (30-sec granularity)

        Raises:
            InvalidDateException: If date format is invalid

        Note:
            The data returned can include a sleep period that began on the previous
            date. For example, requesting logs for 2021-12-22 may return a log entry
            that began on 2021-12-21 but ended on 2021-12-22.
        """
        return self._make_request(
            f"sleep/date/{date}.json",
            user_id=user_id,
            api_version=SleepResource.API_VERSION,
            debug=debug,
        )

    @validate_date_range_params(max_days=100)
    def get_sleep_log_by_date_range(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Gets sleep logs for a date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/sleep/get-sleep-log-by-date-range/

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Sleep logs for the specified date range

        Raises:
            InvalidDateException: If date format is invalid
            InvalidDateRangeException: If start_date is after end_date or date range exceeds 100 days

        Note:
            Maximum date range is 100 days
        """
        return self._make_request(
            f"sleep/date/{start_date}/{end_date}.json",
            user_id=user_id,
            api_version=SleepResource.API_VERSION,
            debug=debug,
        )

    @validate_date_param(field_name="before_date")
    @validate_date_param(field_name="after_date")
    @validate_pagination_params(max_limit=100)
    def get_sleep_log_list(
        self,
        before_date: Optional[str] = None,
        after_date: Optional[str] = None,
        sort: SortDirection = SortDirection.DESCENDING,
        limit: int = 100,
        offset: int = 0,
        user_id: str = "-",
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Gets a list of sleep logs before or after a given date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/sleep/get-sleep-log-list/

        Args:
            before_date: Get entries before this date (YYYY-MM-DD)
            after_date: Get entries after this date (YYYY-MM-DD)
            sort: Sort order ('asc' or 'desc')
            limit: Number of records to return (max 100)
            offset: Offset for pagination (use 0)
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Paginated list of sleep logs

        Note:
            Either before_date or after_date must be specified.
            The offset parameter only supports 0 and using other values may break your application.
            Use the pagination links in the response to iterate through results.

        Raises:
            PaginatonError: If neither before_date nor after_date is specified
            PaginatonError: If offset is not 0
            PaginatonError: If limit exceeds 10
            PaginatonError: If sort is not 'asc' or 'desc'
            PaginatonError: If sort direction doesn't match date parameter
            InvalidDateException: If date format is invalid

        """
        params = {"sort": sort.value, "limit": limit, "offset": offset}
        if before_date:
            params["beforeDate"] = before_date
        if after_date:
            params["afterDate"] = after_date

        return self._make_request(
            "sleep/list.json",
            params=params,
            user_id=user_id,
            api_version=SleepResource.API_VERSION,
            debug=debug,
        )
