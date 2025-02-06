# fitbit_client/resources/body.py

# Standard library imports
from typing import Any
from typing import Dict
from typing import Optional

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import BodyGoalType
from fitbit_client.utils.date_validation import validate_date_param


class BodyResource(BaseResource):
    """
    Handles Fitbit Body API endpoints for managing body measurements.
    API Reference: https://dev.fitbit.com/build/reference/web-api/body/
    """

    def create_bodyfat_goal(
        self, fat: float, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """Create or update a user's body fat goal."""
        return self._make_request(
            "body/log/fat/goal.json",
            params={"fat": fat},
            user_id=user_id,
            http_method="POST",
            debug=debug,
        )

    @validate_date_param()
    def create_bodyfat_log(
        self,
        fat: float,
        date: str,
        time: Optional[str] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a body fat log entry.

        Raises:
            InvalidDateException: If date format is invalid
        """
        params = {"fat": fat, "date": date}
        if time:
            params["time"] = time
        return self._make_request(
            "body/log/fat.json", params=params, user_id=user_id, http_method="POST", debug=debug
        )

    @validate_date_param(field_name="start_date")
    def create_weight_goal(
        self,
        start_date: str,
        start_weight: float,
        weight: Optional[float] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Create or update a user's weight goal.

        Raises:
            InvalidDateException: If start_date format is invalid
        """
        params = {"startDate": start_date, "startWeight": start_weight}
        if weight is not None:
            params["weight"] = weight
        return self._make_request(
            "body/log/weight/goal.json",
            params=params,
            user_id=user_id,
            http_method="POST",
            debug=debug,
        )

    @validate_date_param()
    def create_weight_log(
        self,
        weight: float,
        date: str,
        time: Optional[str] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a weight log entry.

        Raises:
            InvalidDateException: If date format is invalid
        """
        params = {"weight": weight, "date": date}
        if time:
            params["time"] = time
        return self._make_request(
            "body/log/weight.json", params=params, user_id=user_id, http_method="POST", debug=debug
        )

    def delete_bodyfat_log(
        self, bodyfat_log_id: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """Delete a body fat log entry."""
        return self._make_request(
            f"body/log/fat/{bodyfat_log_id}.json",
            user_id=user_id,
            http_method="DELETE",
            debug=debug,
        )

    def delete_weight_log(
        self, weight_log_id: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """Delete a weight log entry."""
        return self._make_request(
            f"body/log/weight/{weight_log_id}.json",
            user_id=user_id,
            http_method="DELETE",
            debug=debug,
        )

    def get_body_goals(
        self, goal_type: BodyGoalType, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """Get a user's body goals."""
        return self._make_request(
            f"body/log/{goal_type.value}/goal.json", user_id=user_id, debug=debug
        )

    @validate_date_param()
    def get_bodyfat_log(self, date: str, user_id: str = "-", debug: bool = False) -> Dict[str, Any]:
        """
        Get a user's body fat logs for a given date.

        Raises:
            InvalidDateException: If date format is invalid
        """
        return self._make_request(f"body/log/fat/date/{date}.json", user_id=user_id, debug=debug)

    @validate_date_param()
    def get_weight_logs(self, date: str, user_id: str = "-", debug: bool = False) -> Dict[str, Any]:
        """
        Get a user's weight logs for a given date.

        Raises:
            InvalidDateException: If date format is invalid
        """
        return self._make_request(f"body/log/weight/date/{date}.json", user_id=user_id, debug=debug)
