# fitbit_client/resources/body.py

# Standard library imports
from typing import Optional
from typing import cast

# Local imports
from fitbit_client.resources._base import BaseResource
from fitbit_client.resources._constants import BodyGoalType
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.types import JSONDict
from fitbit_client.utils.types import ParamDict


class BodyResource(BaseResource):
    """Provides access to Fitbit Body API for managing body measurements and goals.

    This resource handles endpoints for tracking and managing body metrics including
    weight, body fat percentage, and BMI. It supports creating and retrieving logs
    of measurements, setting goals, and accessing historical body data.

    API Reference: https://dev.fitbit.com/build/reference/web-api/body/

    Required Scopes:
      - weight: Required for all endpoints in this resource

    Note:
        All weight and body fat data is returned in the unit system specified by the
        Accept-Language header provided during client initialization (imperial for en_US,
        metric for most other locales). BMI values are calculated automatically from
        weight logs and user profile data.
    """

    def create_bodyfat_goal(self, fat: float, user_id: str = "-", debug: bool = False) -> JSONDict:
        """Creates or updates a user's body fat percentage goal.

        This endpoint allows setting a target body fat percentage goal that will be
        displayed in the Fitbit app and used to track progress over time.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body/create-bodyfat-goal/

        Args:
            fat: Target body fat percentage in the format X.XX (e.g., 22.5 for 22.5%)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: The created body fat percentage goal

        Raises:
            fitbit_client.exceptions.ValidationException: If fat percentage is not in valid range
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            This endpoint requires the 'weight' OAuth scope. Body fat values should be specified
            as a percentage in decimal format (e.g., 22.5 for 22.5%). Typical healthy ranges vary
            by age, gender, and fitness level, but generally fall between 10-30%.
        """
        result = self._make_request(
            "body/log/fat/goal.json",
            params={"fat": fat},
            user_id=user_id,
            http_method="POST",
            debug=debug,
        )
        return cast(JSONDict, result)

    @validate_date_param()
    def create_bodyfat_log(
        self,
        fat: float,
        date: str,
        time: Optional[str] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """Creates a body fat log entry for tracking body composition over time.

        This endpoint allows recording a body fat percentage measurement for a specific
        date and time, which will be displayed in the Fitbit app and used in trends.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body/create-bodyfat-log/

        Args:
            fat: Body fat measurement in the format X.XX (e.g., 22.5 for 22.5%)
            date: Log date in YYYY-MM-DD format or 'today'
            time: Optional time of measurement in HH:mm:ss format. If not provided,
                will default to last second of the day (23:59:59).
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: The created body fat percentage log entry

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.ValidationException: If fat percentage is not in valid range
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            The returned Body Fat Log IDs are unique to the user, but not globally unique.
            The 'source' field will be set to "API" for entries created through this endpoint.
            Multiple entries can be logged for the same day with different timestamps.
        """
        params: ParamDict = {"fat": fat, "date": date}
        if time:
            params["time"] = time
        result = self._make_request(
            "body/log/fat.json", params=params, user_id=user_id, http_method="POST", debug=debug
        )
        return cast(JSONDict, result)

    @validate_date_param(field_name="start_date")
    def create_weight_goal(
        self,
        start_date: str,
        start_weight: float,
        weight: Optional[float] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """Creates or updates a user's weight goal for tracking progress.

        This endpoint sets a target weight goal with starting parameters, which will be
        used to track progress in the Fitbit app and determine recommended weekly changes.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body/create-weight-goal/

        Args:
            start_date: Weight goal start date in YYYY-MM-DD format or 'today'
            start_weight: Starting weight before reaching goal in X.XX format
            weight: Optional target weight goal in X.XX format. Required if user
                doesn't have an existing weight goal.
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: The created weight goal with goal type and recommended changes

        Raises:
            fitbit_client.exceptions.InvalidDateException: If start_date format is invalid
            fitbit_client.exceptions.ValidationException: If weight values are invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Weight values should be specified in the unit system that corresponds
            to the Accept-Language header provided during client initialization
            (pounds for en_US, kilograms for most other locales).

            The goalType is automatically determined by comparing start_weight to weight:
            - If target < start: "LOSE"
            - If target > start: "GAIN"
            - If target = start: "MAINTAIN"
        """
        params: ParamDict = {"startDate": start_date, "startWeight": start_weight}
        if weight is not None:
            params["weight"] = weight
        result = self._make_request(
            "body/log/weight/goal.json",
            params=params,
            user_id=user_id,
            http_method="POST",
            debug=debug,
        )
        return cast(JSONDict, result)

    @validate_date_param()
    def create_weight_log(
        self,
        weight: float,
        date: str,
        time: Optional[str] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """Creates a weight log entry for tracking body weight over time.

        This endpoint allows recording a weight measurement for a specific
        date and time, which will be displayed in the Fitbit app and used to
        calculate BMI and track progress toward weight goals.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body/create-weight-log/

        Args:
            weight: Weight measurement in X.XX format (in kg or lbs based on user settings)
            date: Log date in YYYY-MM-DD format or 'today'
            time: Optional time of measurement in HH:mm:ss format. If not provided,
                will default to last second of the day (23:59:59).
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: The created weight log entry with BMI calculation

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.ValidationException: If weight value is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Weight values should be in the unit system that corresponds to the
            Accept-Language header provided during client initialization
            (pounds for en_US, kilograms for most other locales).

            BMI (Body Mass Index) is automatically calculated using the provided weight
            and the height stored in the user's profile settings. If the user's height
            is not set, BMI will not be calculated.

            The 'source' field will be set to "API" for entries created through this endpoint.
            Multiple weight entries can be logged for the same day with different timestamps.
        """
        params: ParamDict = {"weight": weight, "date": date}
        if time:
            params["time"] = time
        result = self._make_request(
            "body/log/weight.json", params=params, user_id=user_id, http_method="POST", debug=debug
        )
        return cast(JSONDict, result)

    def delete_bodyfat_log(
        self, bodyfat_log_id: str, user_id: str = "-", debug: bool = False
    ) -> None:
        """Deletes a body fat log entry permanently.

        This endpoint permanently removes a body fat percentage measurement from the user's logs.
        Once deleted, the data cannot be recovered.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body/delete-bodyfat-log/

        Args:
            bodyfat_log_id: ID of the body fat log entry to delete
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            None: This endpoint returns an empty response on success

        Raises:
            fitbit_client.exceptions.ValidationException: If bodyfat_log_id is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted
            fitbit_client.exceptions.NotFoundException: If log entry does not exist

        Note:
            Body fat log IDs can be obtained from the get_bodyfat_log method.
            Deleting logs will affect historical averages and trends in the Fitbit app.
            This operation cannot be undone, so use it cautiously.
        """
        result = self._make_request(
            f"body/log/fat/{bodyfat_log_id}.json",
            user_id=user_id,
            http_method="DELETE",
            debug=debug,
        )
        return cast(None, result)

    def delete_weight_log(
        self, weight_log_id: str, user_id: str = "-", debug: bool = False
    ) -> None:
        """Deletes a weight log entry permanently.

        This endpoint permanently removes a weight measurement from the user's logs.
        Once deleted, the data cannot be recovered.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body/delete-weight-log/

        Args:
            weight_log_id: ID of the weight log entry to delete
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            None: This endpoint returns an empty response on success

        Raises:
            fitbit_client.exceptions.ValidationException: If weight_log_id is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted
            fitbit_client.exceptions.NotFoundException: If log entry does not exist

        Note:
            Weight log IDs can be obtained from the get_weight_logs method.
            Deleting logs will affect historical averages, BMI calculations, and
            trend data in the Fitbit app.

            When the most recent weight log is deleted, the previous weight log
            becomes the current weight displayed in the Fitbit app.

            This operation cannot be undone, so use it cautiously.
        """
        result = self._make_request(
            f"body/log/weight/{weight_log_id}.json",
            user_id=user_id,
            http_method="DELETE",
            debug=debug,
        )
        return cast(None, result)

    def get_body_goals(
        self, goal_type: BodyGoalType, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Retrieves a user's body fat percentage or weight goals.

        This endpoint returns the currently set goals for either body fat percentage
        or weight, including target values and, for weight goals, additional parameters
        like start weight and recommended weekly changes.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body/get-body-goals/

        Args:
            goal_type: Type of goal to retrieve (BodyGoalType.FAT or BodyGoalType.WEIGHT)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Goal information for either weight or body fat percentage

        Raises:
            fitbit_client.exceptions.ValidationException: If goal_type is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Weight values are returned in the unit system specified by
            the Accept-Language header provided during client initialization
            (pounds for en_US, kilograms for most other locales).

            The weightThreshold represents the recommended weekly weight change
            (loss or gain) to achieve the goal in a healthy manner. This is
            calculated based on the difference between starting and target weight.

            If no goal has been set for the requested type, an empty goal object
            will be returned.
        """
        result = self._make_request(
            f"body/log/{goal_type.value}/goal.json", user_id=user_id, debug=debug
        )
        return cast(JSONDict, result)

    @validate_date_param()
    def get_bodyfat_log(self, date: str, user_id: str = "-", debug: bool = False) -> JSONDict:
        """Retrieves a user's body fat percentage logs for a specific date.

        This endpoint returns all body fat percentage measurements recorded on the
        specified date, including those logged manually, via the API, or synced from
        compatible scales.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body/get-bodyfat-log/

        Args:
            date: The date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Body fat percentage logs for the specified date

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            The source field indicates how the data was recorded:
            - "API": From Web API or manual entry in the Fitbit app
            - "Aria"/"Aria2": From Fitbit Aria scale
            - "AriaAir": From Fitbit Aria Air scale
            - "Withings": From Withings scale connected to Fitbit

            Body fat percentage is measured differently depending on the source:
            - Bioelectrical impedance for compatible scales
            - User-entered estimates for manual entries

            Multiple logs may exist for the same date if measurements were taken
            at different times or from different sources.
        """
        result = self._make_request(f"body/log/fat/date/{date}.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    @validate_date_param()
    def get_weight_logs(self, date: str, user_id: str = "-", debug: bool = False) -> JSONDict:
        """Retrieves a user's weight logs for a specific date.

        This endpoint returns all weight measurements recorded on the specified date,
        including those logged manually, via the API, or synced from compatible scales.

        API Reference: https://dev.fitbit.com/build/reference/web-api/body/get-weight-log/

        Args:
            date: The date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Weight logs for the specified date with BMI calculations

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            The source field indicates how the data was recorded:
            - "API": From Web API or manual entry in the Fitbit app
            - "Aria"/"Aria2": From Fitbit Aria scale
            - "AriaAir": From Fitbit Aria Air scale
            - "Withings": From Withings scale connected to Fitbit

            Weight values are returned in the unit system specified by the
            Accept-Language header provided during client initialization
            (pounds for en_US, kilograms for most other locales).

            BMI (Body Mass Index) is automatically calculated using the recorded weight
            and the height stored in the user's profile settings.

            The "fat" field is only included when body fat percentage was measured
            along with weight (typically from compatible scales like Aria).

            Multiple logs may exist for the same date if measurements were taken
            at different times or from different sources.
        """
        result = self._make_request(
            f"body/log/weight/date/{date}.json", user_id=user_id, debug=debug
        )
        return cast(JSONDict, result)
