# fitbit_client/resources/sleep.py

# Standard library imports
from typing import Any
from typing import Dict
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union
from typing import cast

# Local imports
from fitbit_client.exceptions import ParameterValidationException
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import SortDirection
from fitbit_client.resources.pagination import create_paginated_iterator
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params
from fitbit_client.utils.pagination_validation import validate_pagination_params
from fitbit_client.utils.types import JSONDict
from fitbit_client.utils.types import ParamDict

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    # Local imports - only imported during type checking
    # Local imports
    from fitbit_client.resources.pagination import PaginatedIterator


class SleepResource(BaseResource):
    """Provides access to Fitbit Sleep API for recording, retrieving and managing sleep data.

    This resource handles endpoints for creating and retrieving sleep logs, setting sleep goals,
    and accessing detailed sleep statistics and patterns. The API provides information about
    sleep duration, efficiency, and stages (light, deep, REM, awake periods).

    API Reference: https://dev.fitbit.com/build/reference/web-api/sleep/

    Required Scopes: sleep

    Note:
        All Sleep endpoints use API version 1.2, unlike most other Fitbit API endpoints
        which use version 1.
    """

    API_VERSION: str = "1.2"

    def create_sleep_goals(
        self, min_duration: int, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """
        Creates or updates a user's sleep duration goal.

        API Reference: https://dev.fitbit.com/build/reference/web-api/sleep/create-sleep-goals/

        Args:
            min_duration: Target sleep duration in minutes (must be positive)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Sleep goal details including minimum duration and update timestamp

        Raises:
            fitbit_client.exceptions.ParameterValidationException: If min_duration is not positive

        Note:
            Sleep goals help users track and maintain healthy sleep habits.
            The typical recommended sleep duration for adults is 420-480 minutes
            (7-8 hours) per night.
        """
        if min_duration <= 0:
            raise ParameterValidationException(
                message="min_duration must be positive", field_name="min_duration"
            )

        result = self._make_request(
            "sleep/goal.json",
            data={"minDuration": min_duration},
            user_id=user_id,
            http_method="POST",
            api_version=SleepResource.API_VERSION,
            debug=debug,
        )
        return cast(JSONDict, result)

    create_sleep_goal = create_sleep_goals  # semantically correct name

    @validate_date_param(field_name="date")
    def create_sleep_log(
        self,
        date: str,
        duration_millis: int,
        start_time: str,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """Creates a manual log entry for a sleep event.

        This endpoint allows creating manual sleep log entries to track sleep that
        wasn't automatically detected by a device. This is useful for tracking naps
        or sleep periods without wearing a tracker.

        API Reference: https://dev.fitbit.com/build/reference/web-api/sleep/create-sleep-log/

        Args:
            date: Log date in YYYY-MM-DD format or 'today'
            duration_millis: Duration in milliseconds (e.g., 28800000 for 8 hours)
            start_time: Sleep start time in HH:mm format (e.g., "23:30")
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Created sleep log entry with sleep metrics and summary information

        Raises:
            fitbit_client.exceptions.ParameterValidationException: If duration_millis is not positive
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.ValidationException: If time or duration is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            - It is NOT possible to create overlapping log entries
            - The dateOfSleep in the response is the date on which the sleep event ends
            - Manual logs default to "classic" type since they lack the device
              heart rate and movement data needed for "stages" type

            Duration is provided in milliseconds (1 hour = 3,600,000 ms), while most of the
            response values are in minutes for easier readability.

            This endpoint uses API version 1.2, unlike most other Fitbit API endpoints.
        """
        if duration_millis <= 0:
            raise ParameterValidationException(
                message="duration_millis must be positive", field_name="duration_millis"
            )

        params: ParamDict = {"startTime": start_time, "duration": duration_millis, "date": date}
        result = self._make_request(
            "sleep.json",
            params=params,
            user_id=user_id,
            http_method="POST",
            api_version=SleepResource.API_VERSION,
            debug=debug,
        )
        return cast(JSONDict, result)

    def delete_sleep_log(self, log_id: int, user_id: str = "-", debug: bool = False) -> None:
        """Deletes a specific sleep log entry permanently.

        This endpoint permanently removes a sleep log entry from the user's history.
        This can be used for both automatically tracked and manually entered sleep logs.

        API Reference: https://dev.fitbit.com/build/reference/web-api/sleep/delete-sleep-log/

        Args:
            log_id: ID of the sleep log to delete
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            None: This endpoint returns an empty response on success

        Raises:
            fitbit_client.exceptions.NotFoundException: If the log ID doesn't exist
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Deleting a sleep log entry permanently removes it from the user's history
            and daily summaries. This operation cannot be undone.

            Sleep log IDs can be obtained from the get_sleep_log_by_date or
            get_sleep_log_list methods.

            This endpoint uses API version 1.2, unlike most other Fitbit API endpoints.
        """
        result = self._make_request(
            f"sleep/{log_id}.json",
            user_id=user_id,
            http_method="DELETE",
            api_version=SleepResource.API_VERSION,
            debug=debug,
        )
        return cast(None, result)

    def get_sleep_goals(self, user_id: str = "-", debug: bool = False) -> JSONDict:
        """Retrieves a user's current sleep goal settings.

        This endpoint returns the user's target sleep duration goal and related settings.

        API Reference: https://dev.fitbit.com/build/reference/web-api/sleep/get-sleep-goals/

        Args:
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Sleep goal details including target sleep duration (in minutes),
                  consistency level, and last update timestamp

        Raises:
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            The minDuration value represents the target sleep duration in minutes.
            Typical recommended sleep durations are:
            - 420-480 minutes (7-8 hours) for adults
            - 540-600 minutes (9-10 hours) for teenagers
            - 600-660 minutes (10-11 hours) for children

            The consistency value indicates the user's adherence to a regular
            sleep schedule over time, with higher values indicating better consistency.

            This endpoint uses API version 1.2, unlike most other Fitbit API endpoints.
        """
        result = self._make_request(
            "sleep/goal.json", user_id=user_id, api_version=SleepResource.API_VERSION, debug=debug
        )
        return cast(JSONDict, result)

    get_sleep_goal = get_sleep_goals  # semantically correct name

    @validate_date_param(field_name="date")
    def get_sleep_log_by_date(self, date: str, user_id: str = "-", debug: bool = False) -> JSONDict:
        """Returns sleep logs for a specific date.

        This endpoint retrieves all sleep logs (both automatically tracked and manually entered)
        for a specific date. The response includes detailed information about sleep duration,
        efficiency, and sleep stages if available.

        API Reference: https://dev.fitbit.com/build/reference/web-api/sleep/get-sleep-log-by-date/

        Args:
            date: The date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Sleep logs and summary for the specified date, including duration, efficiency and sleep stages

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            The data returned includes all sleep periods that ended on the specified date.
            This means a sleep period that began on the previous date but ended on the
            requested date will be included in the response.

            There are two types of sleep data that may be returned:
            - "classic": Basic sleep with 60-second resolution, showing asleep, restless, and awake states
            - "stages": Advanced sleep with 30-second resolution, showing deep, light, REM, and wake stages

            Stages data is only available for compatible devices with heart rate tracking.
            Manual entries always use the "classic" type.

            This endpoint uses API version 1.2, unlike most other Fitbit API endpoints.
        """
        result = self._make_request(
            f"sleep/date/{date}.json",
            user_id=user_id,
            api_version=SleepResource.API_VERSION,
            debug=debug,
        )
        return cast(JSONDict, result)

    @validate_date_range_params(max_days=100)
    def get_sleep_log_by_date_range(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Retrieves sleep logs for a specified date range.

        This endpoint returns all sleep data (including automatically tracked and manually
        entered sleep logs) for the specified date range, with detailed information about
        sleep duration, efficiency, and sleep stages when available.

        API Reference: https://dev.fitbit.com/build/reference/web-api/sleep/get-sleep-log-by-date-range/

        Args:
            start_date: Start date in YYYY-MM-DD format or 'today'
            end_date: End date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Sleep logs for the specified date range with aggregated sleep statistics

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.InvalidDateRangeException: If start_date is after end_date or range exceeds 100 days
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            The maximum date range is 100 days. For longer historical periods, you
            will need to make multiple requests with different date ranges.

            The data returned includes all sleep periods that ended within the
            specified date range. This means a sleep period that began before the
            start_date but ended within the range will be included in the response.

            As with the single-date endpoint, both "classic" and "stages" sleep data
            may be included depending on device compatibility and how the sleep was logged.

            This endpoint uses API version 1.2, unlike most other Fitbit API endpoints.
        """
        result = self._make_request(
            f"sleep/date/{start_date}/{end_date}.json",
            user_id=user_id,
            api_version=SleepResource.API_VERSION,
            debug=debug,
        )
        return cast(JSONDict, result)

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
        as_iterator: bool = False,
    ) -> Union[JSONDict, "PaginatedIterator"]:
        """Retrieves a paginated list of sleep logs filtered by date.

        This endpoint returns sleep logs before or after a specified date with
        pagination support. It provides an alternative to date-based queries
        when working with large amounts of sleep data.

        API Reference: https://dev.fitbit.com/build/reference/web-api/sleep/get-sleep-log-list/

        Args:
            before_date: Get entries before this date in YYYY-MM-DD format
            after_date: Get entries after this date in YYYY-MM-DD format
            sort: Sort direction (SortDirection.ASCENDING or SortDirection.DESCENDING)
            limit: Number of records to return (max 100)
            offset: Offset for pagination (must be 0)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)
            as_iterator: If True, returns a PaginatedIterator instead of the raw response (default: False)

        Returns:
            If as_iterator=False (default):
                JSONDict: Paginated sleep logs with navigation links and sleep entries
            If as_iterator=True:
                PaginatedIterator: An iterator that yields each page of sleep logs

        Raises:
            fitbit_client.exceptions.PaginationError: If parameters are invalid (see Notes)
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Important pagination requirements:
            - Either before_date or after_date MUST be specified (not both)
            - The offset parameter must be 0 (Fitbit API limitation)
            - If before_date is used, sort must be DESCENDING
            - If after_date is used, sort must be ASCENDING

            When using as_iterator=True, you can iterate through all pages like this:
            ```python
            for page in client.get_sleep_log_list(before_date="2025-01-01", as_iterator=True):
                for sleep_entry in page["sleep"]:
                    print(sleep_entry["logId"])
            ```

            This endpoint returns the same sleep data structure as get_sleep_log_by_date,
            but organized in a paginated format rather than grouped by date.

            This endpoint uses API version 1.2, unlike most other Fitbit API endpoints.
        """
        params: ParamDict = {"sort": sort.value, "limit": limit, "offset": offset}
        if before_date:
            params["beforeDate"] = before_date
        if after_date:
            params["afterDate"] = after_date

        endpoint = "sleep/list.json"
        result = self._make_request(
            endpoint,
            params=params,
            user_id=user_id,
            api_version=SleepResource.API_VERSION,
            debug=debug,
        )

        # If debug mode is enabled, result will be None
        if debug or result is None:
            return cast(JSONDict, result)

        # Return as iterator if requested
        if as_iterator:
            return create_paginated_iterator(
                response=cast(JSONDict, result),
                resource=self,
                endpoint=endpoint,
                method_params=params,
                debug=debug,
            )

        return cast(JSONDict, result)
