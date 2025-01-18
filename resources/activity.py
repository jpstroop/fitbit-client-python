# resources/activity.py
# Standard library imports
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

# Local imports
from resources.base import BaseResource
from resources.constants import ActivityGoalType


class ActivityResource(BaseResource):
    """
    Handles Fitbit Activity API endpoints for recording, retrieving and managing
    user activities and goals.
    API Reference: https://dev.fitbit.com/build/reference/web-api/activity/
    """

    def create_activity_goal(
        self, period: str, type: ActivityGoalType, value: int, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Creates or updates a user's daily or weekly activity goal.

        Args:
            period: 'daily' or 'weekly'
            type: Goal type from ActivityGoalType enum
            value: Target value for the goal
            user_id: Optional user ID, defaults to current user
        """
        data = {"type": type.value, "value": value}
        return self._post(f"activities/goals/{period}.json", data=data, user_id=user_id)

    def log_activity(
        self,
        activity_id: Optional[int] = None,
        activity_name: Optional[str] = None,
        manual_calories: Optional[int] = None,
        start_time: str = "",
        duration_millis: int = 0,
        date: str = "",
        distance: Optional[float] = None,
        distance_unit: Optional[str] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Records an activity to the user's log. Can either log a predefined activity by ID
        or a custom activity by name with manual calorie entry.

        Args:
            activity_id: ID of a predefined activity
            activity_name: Name for a custom activity
            manual_calories: Required when logging custom activity
            start_time: Activity start time (HH:mm)
            duration_millis: Duration in milliseconds
            date: Log date (YYYY-MM-DD)
            distance: Optional distance value
            distance_unit: Optional unit for distance
            user_id: Optional user ID, defaults to current user
        """
        data = {"startTime": start_time, "durationMillis": duration_millis, "date": date}

        if activity_id:
            data["activityId"] = activity_id
            if distance is not None:
                data["distance"] = distance
                if distance_unit:
                    data["distanceUnit"] = distance_unit
        elif activity_name and manual_calories:
            data["activityName"] = activity_name
            data["manualCalories"] = manual_calories
        else:
            raise ValueError(
                "Must provide either activity_id or (activity_name and manual_calories)"
            )

        return self._post("activities.json", data=data, user_id=user_id)

    def get_activity_logs(
        self,
        before_date: Optional[str] = None,
        after_date: Optional[str] = None,
        sort: str = "desc",
        limit: int = 100,
        offset: int = 0,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Retrieves a list of user's activity log entries before or after a given day.

        Args:
            before_date: Get entries before this date (YYYY-MM-DD)
            after_date: Get entries after this date (YYYY-MM-DD)
            sort: Sort order ('asc' or 'desc')
            limit: Number of records to return (max 100)
            offset: Offset for pagination
            user_id: Optional user ID, defaults to current user
        """
        params = {"sort": sort, "limit": limit, "offset": offset}
        if before_date:
            params["beforeDate"] = before_date
        if after_date:
            params["afterDate"] = after_date

        return self._get("activities/list.json", params=params, user_id=user_id)

    def add_favorite_activity(self, activity_id: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Adds an activity to the user's list of favorite activities.

        Args:
            activity_id: ID of the activity to favorite
            user_id: Optional user ID, defaults to current user
        """
        return self._post(f"activities/favorite/{activity_id}.json", user_id=user_id)

    def delete_activity_log(self, activity_log_id: str, user_id: str = "-") -> None:
        """
        Deletes a specific activity log entry from the user's activity history.

        Args:
            activity_log_id: ID of the activity log to delete
            user_id: Optional user ID, defaults to current user
        """
        self._delete(f"activities/{activity_log_id}.json", user_id=user_id)

    def delete_favorite_activity(self, activity_id: str, user_id: str = "-") -> None:
        """
        Removes an activity from the user's list of favorite activities.

        Args:
            activity_id: ID of the activity to unfavorite
            user_id: Optional user ID, defaults to current user
        """
        self._delete(f"activities/favorite/{activity_id}.json", user_id=user_id)

    def get_activity_goals(self, period: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Retrieves the user's current activity goals for the specified period.

        Args:
            period: 'daily' or 'weekly'
            user_id: Optional user ID, defaults to current user
        """
        return self._get(f"activities/goals/{period}.json", user_id=user_id)

    def get_activity_summary(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Retrieves a summary of the user's activities for a specific date.

        Args:
            date: Date to get summary for (YYYY-MM-DD)
            user_id: Optional user ID, defaults to current user
        """
        return self._get(f"activities/date/{date}.json", user_id=user_id)

    def get_activity_type(self, activity_id: str) -> Dict[str, Any]:
        """
        Gets the details of a single activity type from Fitbit's activity database.

        Args:
            activity_id: ID of the activity type to retrieve
        """
        return self._get(f"activities/{activity_id}.json", requires_user_id=False)

    def get_activity_types(self) -> List[Dict[str, Any]]:
        """Retrieves the complete list of available activities and their details."""
        return self._get("activities.json", requires_user_id=False)

    def get_favorite_activities(self, user_id: str = "-") -> List[Dict[str, Any]]:
        """
        Gets the list of activities that the user has marked as favorite.

        Args:
            user_id: Optional user ID, defaults to current user
        """
        return self._get("activities/favorite.json", user_id=user_id)

    def get_frequent_activities(self, user_id: str = "-") -> List[Dict[str, Any]]:
        """
        Gets the list of activities that the user logs most frequently.

        Args:
            user_id: Optional user ID, defaults to current user
        """
        return self._get("activities/frequent.json", user_id=user_id)

    def get_recent_activities(self, user_id: str = "-") -> List[Dict[str, Any]]:
        """
        Gets the list of activities that the user has logged recently.

        Args:
            user_id: Optional user ID, defaults to current user
        """
        return self._get("activities/recent.json", user_id=user_id)

    def get_lifetime_stats(self, user_id: str = "-") -> Dict[str, Any]:
        """
        Retrieves the user's lifetime activity statistics and personal records.

        Args:
            user_id: Optional user ID, defaults to current user
        """
        return self._get("activities.json", user_id=user_id)

    def get_activity_tcx(
        self, log_id: str, include_partial_tcx: bool = False, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Retrieves the TCX (Training Center XML) data for a specific activity log. TCX files
        contain GPS, heart rate, and lap data recorded during the logged exercise.

        Args:
            log_id: ID of the activity log to retrieve
            include_partial_tcx: Include TCX points when GPS data is not available
            user_id: Optional user ID, defaults to current user

        Note:
            Requires both 'activity' and 'location' scopes to be authorized.
        """
        params = {"includePartialTCX": include_partial_tcx} if include_partial_tcx else None
        return self._get(f"activities/{log_id}.tcx", params=params, user_id=user_id)
