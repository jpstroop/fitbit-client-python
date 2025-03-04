# fitbit_client/resources/activity.py

# Standard library imports
from typing import Any
from typing import Dict
from typing import Never
from typing import Optional
from typing import cast

# Local imports
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import ActivityGoalPeriod
from fitbit_client.resources.constants import ActivityGoalType
from fitbit_client.resources.constants import SortDirection
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.pagination_validation import validate_pagination_params
from fitbit_client.utils.types import JSONDict
from fitbit_client.utils.types import JSONList


class ActivityResource(BaseResource):
    """Provides access to Fitbit Activity API for managing user activities and goals.

    This resource handles endpoints for recording, retrieving, and managing various
    aspects of user fitness activities including activity logs, goals, favorites,
    and lifetime statistics. It supports creating and deleting activity records,
    managing activity goals, and retrieving detailed activity information.

    API Reference: https://dev.fitbit.com/build/reference/web-api/activity/

    Required Scopes:
        - activity (for most activity endpoints)
        - location (additionally required for get_activity_tcx)

    Note:
        - Activity records include steps, distance, calories, active minutes, and other metrics
        - Activity logs can be created manually or automatically by Fitbit devices
        - Goals can be set on a daily or weekly basis for various activity metrics
        - Lifetime statistics track cumulative totals since the user's account creation
        - Activity types are categorized by intensity level and metabolic equivalent (MET)
        - Favorite activities can be saved for quick access when logging manual activities
        - TCX files (Training Center XML) provide detailed GPS data for activities with location tracking
    """

    def create_activity_goals(
        self,
        period: ActivityGoalPeriod,
        type: ActivityGoalType,
        value: int,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """Creates or updates a user's daily or weekly activity goal.

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity/create-activity-goal/

        Args:
            period: Goal period (ActivityGoalPeriod.DAILY or ActivityGoalPeriod.WEEKLY)
            type: Goal type from ActivityGoalType enum (e.g., ActivityGoalType.STEPS,
                  ActivityGoalType.FLOORS, ActivityGoalType.ACTIVE_MINUTES)
            value: Target value for the goal (must be positive)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Goal object containing the updated activity goals

        Raises:
            fitbit_client.exceptions.ValidationException: If value is not a positive integer

        Note:
            - This endpoint uses units that correspond to the Accept-Language header provided
            - Setting a new goal will override any previously set goal of the same type and period
            - The response includes all current goals for the specified period, not just
              the one being updated
            - Daily goals: typically steps, floors, distance, calories, active minutes
            - Weekly goals: typically steps, floors, distance, active minutes
            - Not all goal types are available for both periods (e.g., calories is daily only)
            - Goal progress can be tracked using the daily activity summary endpoints
        """
        if value <= 0:
            raise ValidationException(
                message="Goal value must be positive",
                status_code=400,
                error_type="validation",
                field_name="value",
            )

        params = {"type": type.value, "value": value}
        result = self._make_request(
            f"activities/goals/{period.value}.json",
            params=params,
            user_id=user_id,
            http_method="POST",
            debug=debug,
        )
        return cast(JSONDict, result)

    create_activity_goal = create_activity_goals  # alias to match docs

    @validate_date_param(field_name="date")
    def create_activity_log(
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
        debug: bool = False,
    ) -> JSONDict:
        """Records an activity to the user's activity log.

        This endpoint can be used in two ways:
        1. Log a predefined activity by specifying activity_id
        2. Log a custom activity by specifying activity_name and manual_calories

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity/create-activity-log/

        Args:
            activity_id: ID of a predefined activity (get IDs from get_activity_type endpoint)
            activity_name: Name for a custom activity (required if activity_id is not provided)
            manual_calories: Calories burned (required when logging custom activity)
            start_time: Activity start time in 24-hour format (HH:mm)
            duration_millis: Duration in milliseconds
            date: Log date in YYYY-MM-DD format or 'today'
            distance: Optional distance value (required for some activity types)
            distance_unit: Optional unit for distance ('steps', 'miles', 'km')
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: The created activity log entry with details of the recorded activity

        Raises:
            ValueError: If neither activity_id nor activity_name/manual_calories pair is provided
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.ValidationException: If required parameters are missing

        Note:
            - You must provide either activity_id OR both activity_name and manual_calories
            - Some activities (like running or cycling) require a distance value
            - The activity will be added to the user's activity history and count toward daily goals
            - Calories and steps in the response may be estimated based on activity type and duration
            - Activity types can be found using get_activity_type and get_frequent_activities endpoints
            - Duration should be in milliseconds (e.g., 30 minutes = 1800000)
            - Start time should be in 24-hour format (e.g., "14:30" for 2:30 PM)
        """
        if activity_id:
            params = {
                "activityId": activity_id,
                "startTime": start_time,
                "durationMillis": duration_millis,
                "date": date,
            }
            if distance is not None:
                params["distance"] = distance
                if distance_unit:
                    params["distanceUnit"] = distance_unit
        elif activity_name and manual_calories:
            params = {
                "activityName": activity_name,
                "manualCalories": manual_calories,
                "startTime": start_time,
                "durationMillis": duration_millis,
                "date": date,
            }
        else:
            raise ValueError(
                "Must provide either activity_id or (activity_name and manual_calories)"
            )

        result = self._make_request(
            "activities.json", params=params, user_id=user_id, http_method="POST", debug=debug
        )
        return cast(JSONDict, result)

    @validate_date_param(field_name="before_date")
    @validate_date_param(field_name="after_date")
    @validate_pagination_params(max_limit=100)
    def get_activity_log_list(
        self,
        before_date: Optional[str] = None,
        after_date: Optional[str] = None,
        sort: SortDirection = SortDirection.DESCENDING,
        limit: int = 100,
        offset: int = 0,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """Returns a list of user's activity log entries before or after a given day.

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity/get-activity-log-list/

        Args:
            before_date: Return entries before this date (YYYY-MM-DD or 'today').
                        You can optionally include time in ISO 8601 format (YYYY-MM-DDThh:mm:ss).
            after_date: Return entries after this date (YYYY-MM-DD or 'today').
                       You can optionally include time in ISO 8601 format (YYYY-MM-DDThh:mm:ss).
            sort: Sort order - must use SortDirection.ASCENDING with after_date and
                 SortDirection.DESCENDING with before_date (default: DESCENDING)
            limit: Number of records to return (max 100, default: 100)
            offset: Offset for pagination (only 0 is reliably supported)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Activity logs matching the criteria with pagination information

        Raises:
            fitbit_client.exceptions.PaginationException: If neither before_date nor after_date is specified
            fitbit_client.exceptions.PaginationException: If limit exceeds 100 or sort direction is invalid
            fitbit_client.exceptions.InvalidDateException: If date format is invalid

        Note:
            - Either before_date or after_date must be specified, but not both
            - The offset parameter only reliably supports 0; use the "next" URL in the
              pagination response to iterate through results
            - Includes both manual and automatic activity entries
            - Each activity entry contains detailed information about the activity, including
              duration, calories, heart rate (if available), steps, and other metrics
            - Activities are categorized based on Fitbit's internal activity type system
            - The source field indicates whether the activity was logged manually by the user
              or automatically by a Fitbit device
        """
        params = {"sort": sort.value, "limit": limit, "offset": offset}
        if before_date:
            params["beforeDate"] = before_date
        if after_date:
            params["afterDate"] = after_date

        result = self._make_request(
            "activities/list.json", params=params, user_id=user_id, debug=debug
        )
        return cast(JSONDict, result)

    def create_favorite_activity(
        self, activity_id: int, user_id: str = "-", debug: bool = False
    ) -> Dict[Never, Never]:
        """Adds an activity to the user's list of favorite activities.

        Favorite activities appear in a special section of the Fitbit app and website,
        making them easier to access when logging manual activities.

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity/create-favorite-activity/

        Args:
            activity_id: ID of the activity to favorite (get IDs from get_activity_type endpoint)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Dict[Never, Never]: Empty dictionary on success, with HTTP 201 status code

        Raises:
            fitbit_client.exceptions.InvalidRequestException: If activity_id is invalid
            fitbit_client.exceptions.AuthorizationException: If not authorized to access the user

        Note:
            - Favorites are used to quickly access common activities when logging manually
            - Activity IDs can be obtained from get_activity_type or get_frequent_activities endpoints
            - Users can have multiple favorite activities
            - Favorites are displayed prominently in the Fitbit app's manual activity logging UI
            - To retrieve the list of favorites, use the get_favorite_activities endpoint
        """
        result = self._make_request(
            f"activities/favorite/{activity_id}.json",
            user_id=user_id,
            http_method="POST",
            debug=debug,
        )
        return cast(Dict[Never, Never], result)

    def delete_activity_log(
        self, activity_log_id: int, user_id: str = "-", debug: bool = False
    ) -> Dict[Never, Never]:
        """Deletes a specific activity log entry from the user's activity history.

        This endpoint permanently removes an activity from the user's activity history.
        Once deleted, the activity will no longer contribute to the user's daily totals
        or achievements.

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity/delete-activity-log/

        Args:
            activity_log_id: ID of the activity log to delete (obtain from get_activity_log_list)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Dict[Never, Never]: Empty dictionary on success, with HTTP 204 status code

        Raises:
            fitbit_client.exceptions.InvalidRequestException: If activity_log_id is invalid
            fitbit_client.exceptions.NotFoundException: If the activity log doesn't exist
            fitbit_client.exceptions.AuthorizationException: If not authorized to delete this activity

        Note:
            - Only manually logged activities can be deleted
            - Automatic activities detected by Fitbit devices cannot be deleted
            - Activity log IDs can be obtained from the get_activity_log_list endpoint
            - Deleting an activity permanently removes it from the user's history
            - Deletion immediately affects daily totals, goals, and achievements
            - The deletion cannot be undone
        """
        result = self._make_request(
            f"activities/{activity_log_id}.json", user_id=user_id, http_method="DELETE", debug=debug
        )
        return cast(Dict[Never, Never], result)

    def delete_favorite_activity(
        self, activity_id: int, user_id: str = "-", debug: bool = False
    ) -> None:
        """Removes an activity from the user's list of favorite activities.

        This endpoint unfavorites a previously favorited activity. The activity will
        still be available for logging but will no longer appear in the favorites list.

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity/delete-favorite-activity/

        Args:
            activity_id: ID of the activity to unfavorite
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            None: Returns None on success with HTTP 204 status code

        Raises:
            fitbit_client.exceptions.InvalidRequestException: If activity_id is invalid
            fitbit_client.exceptions.NotFoundException: If the activity is not in favorites list
            fitbit_client.exceptions.AuthorizationException: If not authorized to access the user

        Note:
            - Removing a favorite doesn't delete the activity type, just removes it from favorites
            - To get the list of current favorites, use the get_favorite_activities endpoint
            - Activity IDs can be obtained from the get_favorite_activities response
            - Unfavoriting an activity only affects the UI display in the Fitbit app
        """
        result = self._make_request(
            f"activities/favorite/{activity_id}.json",
            user_id=user_id,
            http_method="DELETE",
            debug=debug,
        )
        return cast(None, result)

    def get_activity_goals(
        self, period: ActivityGoalPeriod, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Returns the user's current activity goals for the specified period.

        This endpoint retrieves the user's activity goals which are targets for steps,
        distance, floors, active minutes, and calories that the user aims to achieve
        within the specified time period (daily or weekly).

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity/get-activity-goals/

        Args:
            period: Goal period - either ActivityGoalPeriod.DAILY or ActivityGoalPeriod.WEEKLY
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: The current activity goals containing targets for metrics like steps,
                  distance, floors, active minutes, and calories

        Raises:
            fitbit_client.exceptions.InvalidRequestException: If period is invalid
            fitbit_client.exceptions.AuthorizationException: If not authorized to access this user's data

        Note:
            - Daily and weekly goals may have different available metrics
            - Daily goals typically include: steps, floors, distance, active minutes, calories
            - Weekly goals typically include: steps, floors, distance, active minutes (no calories)
            - Units (miles/km) depend on the user's account settings
            - Goals can be updated using the create_activity_goals endpoint
            - The response will only include goals that have been set for the specified period
        """
        result = self._make_request(
            f"activities/goals/{period.value}.json", user_id=user_id, debug=debug
        )
        return cast(JSONDict, result)

    @validate_date_param()
    def get_daily_activity_summary(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Returns a summary of the user's activities for a specific date.

        This endpoint provides a comprehensive summary of all activity metrics for the specified
        date, including activity logs, goals, and daily totals for steps, distance, calories, and
        active minutes. It serves as a convenient way to get a complete picture of a user's
        activity for a single day.

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity/get-daily-activity-summary/

        Args:
            date: Date to get summary for (YYYY-MM-DD or 'today')
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Activity summary for the specified date containing logged activities,
                  daily goals, and summary metrics (steps, distance, calories, minutes at
                  different activity levels)

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid

        Note:
            The response includes data in the unit system specified by the Accept-Language header.
            Daily summary data for elevation (elevation, floors) is only included for users with
            a device that has an altimeter. Goals are included only for today and up to 21 days
            in the past. The goals section will only include goals that have been set by the user.
            Active minutes include veryActiveMinutes, fairlyActiveMinutes, and lightlyActiveMinutes.
        """
        result = self._make_request(f"activities/date/{date}.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    def get_activity_type(self, activity_id: int, debug: bool = False) -> JSONDict:
        """Returns the details of a single activity type from Fitbit's activity database.

        This endpoint retrieves information about a specific activity type including its name,
        description, and MET (Metabolic Equivalent of Task) value. Activity types are
        standardized categories like "Running", "Swimming", or "Yoga" that can be used
        when logging activities.

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity/get-activity-type/

        Args:
            activity_id: ID of the activity type to retrieve
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Activity type details including name, description, MET values, and
                  different intensity levels (light, moderate, vigorous)

        Raises:
            fitbit_client.exceptions.InvalidRequestException: If activity_id is invalid
            fitbit_client.exceptions.NotFoundException: If the activity type doesn't exist

        Note:
            - This endpoint doesn't require a user_id as it accesses the global activity database
            - MET values represent the energy cost of activities (higher values = more intense)
            - Activity types are used when logging manual activities via create_activity_log
            - To find activity IDs, use get_all_activity_types or get_frequent_activities
            - The hasSpeed field indicates whether the activity supports distance tracking
            - Activity levels (Light, Moderate, Vigorous) represent intensity variations
        """
        result = self._make_request(
            f"activities/{activity_id}.json", requires_user_id=False, debug=debug
        )
        return cast(JSONDict, result)

    def get_all_activity_types(self, debug: bool = False) -> JSONDict:
        """Returns the complete list of all available activity types in Fitbit's database.

        This endpoint retrieves a comprehensive list of standardized activity types that
        can be used when logging manual activities. Each activity includes its ID, name,
        description, and MET (Metabolic Equivalent of Task) values.

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity/get-all-activity-types/

        Args:
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Complete list of activity types organized by categories (Cardio, Sports, etc.),
                  with each activity containing its ID, name, description, and MET value

        Raises:
            fitbit_client.exceptions.AuthorizationException: If not authorized to access the API

        Note:
            - This endpoint doesn't require a user_id as it accesses the global activity database
            - Activities are organized into categories (e.g., Cardio, Sports, Water Activities)
            - The response can be large as it contains all available activities
            - Use the activity IDs from this response when calling create_activity_log
            - For a more manageable list, consider using get_frequent_activities instead
            - MET values indicate intensity (higher values = more intense activity)
        """
        result = self._make_request("activities.json", requires_user_id=False, debug=debug)
        return cast(JSONDict, result)

    def get_favorite_activities(self, user_id: str = "-", debug: bool = False) -> JSONList:
        """Returns the list of activities that the user has marked as favorites.

        Favorite activities are those the user has explicitly marked for quick access
        when manually logging activities. These appear in a dedicated section of the
        activity logging interface in the Fitbit app.

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity/get-favorite-activities/

        Args:
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONList: List of favorite activities with details including activity ID, name,
                  description, MET value, and when the activity was added as a favorite

        Raises:
            fitbit_client.exceptions.AuthorizationException: If not authorized to access the user's data

        Note:
            - Favorites are used for quick access when logging manual activities
            - Activities can be added to favorites using create_favorite_activity
            - Activities can be removed from favorites using delete_favorite_activity
            - The dateAdded field shows when the activity was marked as favorite
            - The calories field shows an estimate based on the activity's MET value
            - If the user has no favorites, an empty array is returned
        """
        result = self._make_request("activities/favorite.json", user_id=user_id, debug=debug)
        return cast(JSONList, result)

    def get_frequent_activities(self, user_id: str = "-", debug: bool = False) -> JSONList:
        """Returns the list of activities that the user logs most frequently.

        This endpoint provides a personalized list of activities based on the user's
        activity logging history. It helps provide quick access to activities the user
        regularly logs, even if they're not explicitly marked as favorites.

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity/get-frequent-activities/

        Args:
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONList: List of frequently logged activities with details including activity ID,
                  name, description, MET value, and typical metrics like duration and distance

        Raises:
            fitbit_client.exceptions.AuthorizationException: If not authorized to access the user's data

        Note:
            - This list is automatically generated based on the user's activity logging patterns
            - Unlike favorites, users cannot directly add or remove activities from this list
            - Activities with most logged instances appear in this list
            - The dateAdded field shows when the activity was most recently logged
            - If the user has no activity history, an empty array is returned
            - This list is a good source of relevant activity IDs for create_activity_log
        """
        result = self._make_request("activities/frequent.json", user_id=user_id, debug=debug)
        return cast(JSONList, result)

    def get_recent_activity_types(self, user_id: str = "-", debug: bool = False) -> JSONList:
        """Returns the list of activities that the user has logged recently.

        This endpoint retrieves activities that the user has manually logged in the
        recent past, sorted by most recent first. It provides a chronological view
        of the user's activity logging history.

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity/get-recent-activity-types/

        Args:
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONList: List of recently logged activities with details including activity ID, name,
                  description, MET value, and when each activity was logged

        Raises:
            fitbit_client.exceptions.AuthorizationException: If not authorized to access the user's data

        Note:
            - Activities are listed in reverse chronological order (newest first)
            - Only manually logged activities appear in this list
            - The dateAdded field shows when the activity was logged
            - If the user has no recent activity logs, an empty array is returned
            - This list differs from get_activity_log_list which shows actual activity instances
            - Unlike favorites, this list is purely historical and not for quick access
        """
        result = self._make_request("activities/recent.json", user_id=user_id, debug=debug)
        return cast(JSONList, result)

    def get_lifetime_stats(self, user_id: str = "-", debug: bool = False) -> JSONDict:
        """Returns the user's lifetime activity statistics and personal records.

        This endpoint provides cumulative totals of steps, distance, floors, and active minutes,
        as well as personal activity records like "most steps in one day".

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity/get-lifetime-stats/

        Args:
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Lifetime statistics containing cumulative totals (steps, distance, floors)
                  and personal records (best days) for various activity metrics, divided into
                  "total" (all activities) and "tracker" (device-tracked only) categories

        Raises:
            fitbit_client.exceptions.AuthorizationException: If not authorized to access this user's data

        Note:
            - "Total" includes manually logged activities, while "tracker" only includes device-tracked data
            - A value of -1 indicates that the metric is not available
            - The "best" section contains personal records with dates and values
            - Units (miles/km) depend on the user's account settings
            - Lifetime stats accumulate from the date the user created their Fitbit account
            - Stats are updated in near real-time as new activities are recorded
        """
        result = self._make_request("activities.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    def get_activity_tcx(
        self,
        log_id: int,
        include_partial_tcx: bool = False,
        user_id: str = "-",
        debug: bool = False,
    ) -> str:
        """Returns the TCX (Training Center XML) data for a specific activity log.

        TCX (Training Center XML) is a data exchange format developed by Garmin that contains
        detailed GPS coordinates, heart rate data, lap information, and other metrics recorded
        during GPS-tracked activities like running, cycling, or walking.

        API Reference: https://dev.fitbit.com/build/reference/web-api/activity/get-activity-tcx/

        Args:
            log_id: ID of the activity log to retrieve (obtain from get_activity_log_list)
            include_partial_tcx: Include TCX points even when GPS data is not available (default: False)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            str: Raw XML string containing TCX data in Training Center XML format

        Raises:
            fitbit_client.exceptions.InvalidRequestException: If log_id is invalid
            fitbit_client.exceptions.NotFoundException: If the activity log doesn't exist
            fitbit_client.exceptions.InsufficientScopeException: If location scope is not authorized

        Note:
            - Requires both 'activity' and 'location' OAuth scopes to be authorized
            - The log must be from a GPS-tracked activity (e.g., running, cycling with GPS enabled)
            - TCX data includes timestamps, GPS coordinates, elevation, heart rate, and lap data
            - TCX files can be imported into third-party fitness analysis tools
            - Setting include_partial_tcx=True will include points even if GPS signal was lost
            - Not all activities have TCX data available (e.g., manually logged activities)
            - To check if an activity has GPS data, look for hasGps=True in the activity log
        """
        params = {"includePartialTCX": include_partial_tcx} if include_partial_tcx else None
        result = self._make_request(
            f"activities/{log_id}.tcx", params=params, user_id=user_id, debug=debug
        )
        return cast(str, result)
