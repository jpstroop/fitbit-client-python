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

    This resource provides endpoints for managing:
    - Body fat logs and goals
    - Weight logs and goals
    - BMI data (derived from weight logs)

    All data is returned in the unit system specified by the Accept-Language header.

    API Reference: https://dev.fitbit.com/build/reference/web-api/body/

    Scope: weight
    """

    def create_bodyfat_goal(
        self, fat: float, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Create or update a user's body fat goal.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body/create-bodyfat-goal/

        Args:
            fat: Target body fat percentage in the format X.XX
            user_id: Optional user ID. Use "-" (dash) for current logged-in user.
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Dict containing goal object with the updated body fat target value

        Raises:
            ValidationException: If fat percentage is not in valid range
            AuthorizationException: If required scope is not granted
        """
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

        API Reference: https://dev.fitbit.com/build/reference/web-api/body/create-bodyfat-log/

        Args:
            fat: Body fat measurement in the format X.XX
            date: Log date in YYYY-MM-DD format
            time: Optional time of measurement in HH:mm:ss format. If not provided,
                will default to last second of the day.
            user_id: Optional user ID. Use "-" (dash) for current logged-in user.
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Dict containing the created log entry including:
            - date: The date the measurement was recorded
            - fat: The body fat percentage
            - logId: Unique identifier for the log entry
            - source: Origin of the data (e.g., "API")
            - time: Time the measurement was recorded

        Raises:
            InvalidDateException: If date format is invalid
            ValidationException: If fat percentage is not in valid range
            AuthorizationException: If required scope is not granted

        Note:
            The returned Body Fat Log IDs are unique to the user, but not globally unique.
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

        API Reference: https://dev.fitbit.com/build/reference/web-api/body/create-weight-goal/

        Args:
            start_date: Weight goal start date in YYYY-MM-DD format
            start_weight: Starting weight before reaching goal in X.XX format
            weight: Optional target weight goal in X.XX format. Required if user
                doesn't have an existing weight goal.
            user_id: Optional user ID. Use "-" (dash) for current logged-in user.
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Dict containing weight goal details including:
            - goalType: The type of goal (e.g., "LOSE")
            - startDate: Goal start date
            - startWeight: Initial weight
            - weight: Target weight
            - weightThreshold: Recommended weekly weight change

        Raises:
            InvalidDateException: If start_date format is invalid
            ValidationException: If weight values are invalid
            AuthorizationException: If required scope is not granted

        Note:
            Weight values should be specified in the unit system that corresponds
            to the Accept-Language header provided during client initialization.
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

        API Reference: https://dev.fitbit.com/build/reference/web-api/body/create-weight-log/

        Args:
            weight: Weight measurement in X.XX format
            date: Log date in YYYY-MM-DD format
            time: Optional time of measurement in HH:mm:ss format. If not provided,
                will default to last second of the day.
            user_id: Optional user ID. Use "-" (dash) for current logged-in user.
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Dict containing the created log entry including:
            - bmi: Calculated BMI
            - date: Log entry date
            - logId: Unique identifier for the weight log
            - source: Origin of the data (e.g., "API")
            - time: Time of measurement
            - weight: Weight value

        Raises:
            InvalidDateException: If date format is invalid
            ValidationException: If weight value is invalid
            AuthorizationException: If required scope is not granted

        Note:
            Weight values should be in the unit system that corresponds to the
            Accept-Language header provided during client initialization.
            Weight Log IDs are unique to the user but not globally unique.
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
        """
        Delete a body fat log entry.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body/delete-bodyfat-log/

        Args:
            bodyfat_log_id: ID of the body fat log entry to delete
            user_id: Optional user ID. Use "-" (dash) for current logged-in user.
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Empty dict on success

        Raises:
            ValidationException: If bodyfat_log_id is invalid
            AuthorizationException: If required scope is not granted
            NotFoundException: If log entry does not exist
        """
        return self._make_request(
            f"body/log/fat/{bodyfat_log_id}.json",
            user_id=user_id,
            http_method="DELETE",
            debug=debug,
        )

    def delete_weight_log(
        self, weight_log_id: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Delete a weight log entry.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body/delete-weight-log/

        Args:
            weight_log_id: ID of the weight log entry to delete
            user_id: Optional user ID. Use "-" (dash) for current logged-in user.
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Empty dict on success

        Raises:
            ValidationException: If weight_log_id is invalid
            AuthorizationException: If required scope is not granted
            NotFoundException: If log entry does not exist
        """
        return self._make_request(
            f"body/log/weight/{weight_log_id}.json",
            user_id=user_id,
            http_method="DELETE",
            debug=debug,
        )

    def get_body_goals(
        self, goal_type: BodyGoalType, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Get a user's body fat or weight goals.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body/get-body-goals/

        Args:
            goal_type: Type of goal to retrieve (fat or weight)
            user_id: Optional user ID. Use "-" (dash) for current logged-in user.
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Dict containing goal information. For weight goals includes:
            - goalType: Type of goal (e.g., "LOSE")
            - startDate: Goal start date
            - startWeight: Initial weight
            - weight: Target weight
            - weightThreshold: Recommended weekly weight change

            For fat goals includes:
            - fat: Target body fat percentage

        Raises:
            ValidationException: If goal_type is invalid
            AuthorizationException: If required scope is not granted

        Note:
            All weight values are returned in the unit system specified by
            the Accept-Language header provided during client initialization.
        """
        return self._make_request(
            f"body/log/{goal_type.value}/goal.json", user_id=user_id, debug=debug
        )

    @validate_date_param()
    def get_bodyfat_log(self, date: str, user_id: str = "-", debug: bool = False) -> Dict[str, Any]:
        """
        Get a user's body fat logs for a given date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body/get-bodyfat-log/

        Args:
            date: The date in YYYY-MM-DD format
            user_id: Optional user ID. Use "-" (dash) for current logged-in user.
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Dict containing list of fat logs for the date, each including:
            - date: When the measurement was recorded
            - fat: Body fat percentage
            - logId: Unique identifier for this log entry
            - source: Origin of the data (e.g., "API", "Aria")
            - time: Time of measurement

        Raises:
            InvalidDateException: If date format is invalid
            AuthorizationException: If required scope is not granted

        Note:
            The source field indicates how the data was recorded:
            - "API": From Web API or manual entry
            - "Aria"/"Aria2": From Fitbit Aria scale
            - "AriaAir": From Fitbit Aria Air scale
            - "Withings": From Withings scale
        """
        return self._make_request(f"body/log/fat/date/{date}.json", user_id=user_id, debug=debug)

    @validate_date_param()
    def get_weight_logs(self, date: str, user_id: str = "-", debug: bool = False) -> Dict[str, Any]:
        """
        Get a user's weight logs for a given date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body/get-weight-log/

        Args:
            date: The date in YYYY-MM-DD format
            user_id: Optional user ID. Use "-" (dash) for current logged-in user.
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Dict containing list of weight logs for the date, each including:
            - bmi: Calculated BMI value
            - date: When the measurement was recorded
            - logId: Unique identifier for this log entry
            - source: Origin of the data (e.g., "API", "Aria")
            - time: Time of measurement
            - weight: Weight value in specified unit system
            - fat: Body fat percentage if available

        Raises:
            InvalidDateException: If date format is invalid
            AuthorizationException: If required scope is not granted

        Note:
            The source field indicates how the data was recorded:
            - "API": From Web API or manual entry
            - "Aria"/"Aria2": From Fitbit Aria scale
            - "AriaAir": From Fitbit Aria Air scale
            - "Withings": From Withings scale

            Weight values are returned in the unit system specified by the
            Accept-Language header provided during client initialization.
        """
        return self._make_request(f"body/log/weight/date/{date}.json", user_id=user_id, debug=debug)
