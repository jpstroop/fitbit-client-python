# resources/body.py
# Standard library imports
from typing import Any
from typing import Dict
from typing import Optional

# Local imports
from resources.base import BaseResource
from resources.constants import BodyGoalType


class BodyResource(BaseResource):
    """
    Handles Fitbit Body API endpoints for managing body measurements.
    API Reference: https://dev.fitbit.com/build/reference/web-api/body/
    """

    def create_body_fat_goal(self, fat: float, user_id: str = "-") -> Dict[str, Any]:
        """
        Create or update a user's body fat goal.

        Args:
            fat: Target body fat percentage in the format X.XX
            user_id: Optional user ID, defaults to current user

        Returns:
            Response contains goal object with the fat value
        """
        return self._post("body/log/fat/goal.json", params={"fat": fat}, user_id=user_id)

    def create_body_fat_log(
        self, fat: float, date: str, time: Optional[str] = None, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Create a body fat log entry.

        Args:
            fat: Body fat measurement in the format X.XX
            date: Log date in YYYY-MM-DD format
            time: Optional time in HH:mm:ss format. If not provided, the timestamp
                 will be the last second of the day.
            user_id: Optional user ID, defaults to current user

        Returns:
            Response contains the fat log object with the created entry
        """
        params = {"fat": fat, "date": date}
        if time:
            params["time"] = time
        return self._post("body/log/fat.json", params=params, user_id=user_id)

    def create_weight_goal(
        self,
        start_date: str,
        start_weight: float,
        weight: Optional[float] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Create or update a user's weight goal.

        Args:
            start_date: Start date in YYYY-MM-DD format
            start_weight: Starting weight in the format X.XX
            weight: Target weight in the format X.XX (required if no existing goal)
            user_id: Optional user ID, defaults to current user

        Returns:
            Response contains the weight goal object
        """
        params = {"startDate": start_date, "startWeight": start_weight}
        if weight is not None:
            params["weight"] = weight
        return self._post("body/log/weight/goal.json", params=params, user_id=user_id)

    def create_weight_log(
        self, weight: float, date: str, time: Optional[str] = None, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Create a weight log entry.

        Args:
            weight: Weight in the format X.XX
            date: Log date in YYYY-MM-DD format
            time: Optional time in HH:mm:ss format. If not provided, the timestamp
                 will be the last second of the day.
            user_id: Optional user ID, defaults to current user

        Returns:
            Response contains the weight log object with the created entry
        """
        params = {"weight": weight, "date": date}
        if time:
            params["time"] = time
        return self._post("body/log/weight.json", params=params, user_id=user_id)

    def delete_body_fat_log(self, body_fat_log_id: str, user_id: str = "-") -> None:
        """
        Delete a body fat log entry.

        Args:
            body_fat_log_id: ID of the log entry to delete
            user_id: Optional user ID, defaults to current user
        """
        self._delete(f"body/log/fat/{body_fat_log_id}.json", user_id=user_id)

    def delete_weight_log(self, weight_log_id: str, user_id: str = "-") -> None:
        """
        Delete a weight log entry.

        Args:
            weight_log_id: ID of the log entry to delete
            user_id: Optional user ID, defaults to current user
        """
        self._delete(f"body/log/weight/{weight_log_id}.json", user_id=user_id)

    def get_body_goals(self, goal_type: BodyGoalType, user_id: str = "-") -> Dict[str, Any]:
        """
        Get a user's body goals.

        Args:
            goal_type: Type of goal - either 'weight' or 'fat'
            user_id: Optional user ID, defaults to current user

        Returns:
            Response contains the goal object for the specified type
        """
        return self._get(f"body/log/{goal_type.value}/goal.json", user_id=user_id)

    def get_body_fat_logs(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Get a user's body fat logs for a given date.

        Args:
            date: The date in YYYY-MM-DD format
            user_id: Optional user ID, defaults to current user

        Returns:
            Response contains a list of body fat log entries for the date
        """
        return self._get(f"body/log/fat/date/{date}.json", user_id=user_id)

    def get_weight_logs(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Get a user's weight logs for a given date.

        Args:
            date: The date in YYYY-MM-DD format
            user_id: Optional user ID, defaults to current user

        Returns:
            Response contains a list of weight log entries for the date
        """
        return self._get(f"body/log/weight/date/{date}.json", user_id=user_id)
