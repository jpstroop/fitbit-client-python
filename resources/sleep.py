# resources/sleep.py
# Standard library imports
from typing import Any
from typing import Dict
from typing import Optional

# Local imports
from resources.base import BaseResource
from resources.constants import SleepType


class SleepResource(BaseResource):
    """
    Handles Fitbit Sleep API endpoints for recording, retrieving and managing
    user sleep data and goals.

    API Reference: https://dev.fitbit.com/build/reference/web-api/sleep/
    """

    def create_sleep_goal(self, min_duration: int, user_id: str = "-") -> Dict[str, Any]:
        """
        Creates or updates a user's sleep goal.

        Args:
            min_duration: Length of sleep goal in minutes
            user_id: Optional user ID, defaults to current user

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
        )

    def log_sleep(
        self,
        start_time: str,
        duration_millis: int,
        date: str,
        sleep_type: SleepType = SleepType.CLASSIC,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Creates a log entry for a sleep event.

        Args:
            start_time: Activity start time (HH:mm)
            duration_millis: Duration in milliseconds
            date: Log date in YYYY-MM-DD format
            sleep_type: Type of sleep log (classic or stages)
            user_id: Optional user ID, defaults to current user

        Returns:
            Created sleep log entry details

        Note:
            - It is NOT possible to create overlapping log entries
            - The dateOfSleep in the response is the date on which the sleep event ends
            - Manual logs default to "classic" type since they lack the device
              heart rate and movement data needed for "stages" type
        """
        if duration_millis <= 0:
            raise ValueError("duration_millis must be positive")

        params = {
            "startTime": start_time,
            "duration": duration_millis,
            "date": date,
            "type": sleep_type.value,
        }
        return self._make_request("sleep.json", params=params, user_id=user_id, http_method="POST")

    def delete_sleep_log(self, log_id: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Deletes a specific sleep log entry.

        Args:
            log_id: ID of the sleep log to delete
            user_id: Optional user ID, defaults to current user
        """
        return self._make_request(f"sleep/{log_id}.json", user_id=user_id, http_method="DELETE")

    def get_sleep_goal(self, user_id: str = "-") -> Dict[str, Any]:
        """
        Gets a user's current sleep goal.

        Args:
            user_id: Optional user ID, defaults to current user

        Returns:
            Sleep goal details including:
            - minDuration: Length of sleep goal in minutes
            - consistency: Sleep goal consistency flow status
            - updatedOn: Last update timestamp
        """
        return self._make_request("sleep/goal.json", user_id=user_id)

    def get_sleep_logs(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Gets sleep logs for a specific date.

        Args:
            date: The date in YYYY-MM-DD format
            user_id: Optional user ID, defaults to current user

        Returns:
            Sleep logs and summary for the specified date including:
            - Classic logs: asleep, restless, awake levels (60-sec granularity)
            - Stages logs: deep, light, rem, wake levels (30-sec granularity)

        Note:
            The data returned can include a sleep period that began on the previous
            date. For example, requesting logs for 2021-12-22 may return a log entry
            that began on 2021-12-21 but ended on 2021-12-22.
        """
        return self._make_request(f"sleep/date/{date}.json", user_id=user_id)

    def get_sleep_logs_by_date_range(
        self, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Gets sleep logs for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            user_id: Optional user ID, defaults to current user

        Returns:
            Sleep logs for the specified date range

        Note:
            Maximum date range is 100 days
        """
        return self._make_request(f"sleep/date/{start_date}/{end_date}.json", user_id=user_id)

    def get_sleep_logs_list(
        self,
        before_date: Optional[str] = None,
        after_date: Optional[str] = None,
        sort: str = "desc",
        limit: int = 100,
        offset: int = 0,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Gets a list of sleep logs before or after a given date.

        Args:
            before_date: Get entries before this date (YYYY-MM-DD)
            after_date: Get entries after this date (YYYY-MM-DD)
            sort: Sort order ('asc' or 'desc')
            limit: Number of records to return (max 100)
            offset: Offset for pagination (use 0)
            user_id: Optional user ID, defaults to current user

        Returns:
            Paginated list of sleep logs

        Note:
            - Either before_date or after_date must be specified
            - Use sort='desc' with before_date and sort='asc' with after_date
            - For pagination, use the next/previous links in the pagination response
              object rather than manually specifying offset
        """
        if not before_date and not after_date:
            raise ValueError("Must specify either before_date or after_date")

        if limit > 100:
            raise ValueError("Maximum limit is 100")

        if sort not in ("asc", "desc"):
            raise ValueError("Sort must be either 'asc' or 'desc'")

        # Validate sort direction matches date parameter
        if before_date and sort != "desc":
            raise ValueError("Must use sort='desc' with before_date")
        if after_date and sort != "asc":
            raise ValueError("Must use sort='asc' with after_date")

        params = {"sort": sort, "limit": limit, "offset": offset}
        if before_date:
            params["beforeDate"] = before_date
        if after_date:
            params["afterDate"] = after_date

        return self._make_request("sleep/list.json", params=params, user_id=user_id)
