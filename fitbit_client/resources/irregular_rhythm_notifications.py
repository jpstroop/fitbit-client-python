# fitbit_client/resources/irregular_rhythm_notifications.py

# Standard library imports
from typing import Optional
from typing import cast

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import SortDirection
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.pagination_validation import validate_pagination_params
from fitbit_client.utils.types import JSONDict
from fitbit_client.utils.types import ParamDict


class IrregularRhythmNotificationsResource(BaseResource):
    """Provides access to Fitbit Irregular Rhythm Notifications (IRN) API for heart rhythm monitoring.

    This resource handles endpoints for retrieving Irregular Rhythm Notifications (IRN),
    which are alerts sent to users when their device detects signs of atrial fibrillation (AFib).
    The API can be used to access notification history and user enrollment status.

    API Reference: https://dev.fitbit.com/build/reference/web-api/irregular-rhythm-notifications/

    Required Scopes:
        - irregular_rhythm_notifications (for all IRN endpoints)

    Important:
        The IRN API is for research use or investigational use only, and is not intended
        for clinical or diagnostic purposes. IRN results do not replace traditional diagnosis
        methods and should not be interpreted as medical advice.

    Note:
        - Only alerts that have been read by the user in the Fitbit app are accessible
        - IRN does not support subscription notifications (webhooks)
        - Data becomes available after device sync and user interaction with notifications
        - IRN requires a compatible Fitbit device with heart rate monitoring capabilities
        - Users must complete an on-device enrollment flow to enable the IRN feature
        - Notifications are analyzed based on heart rate data collected during sleep
        - IRN is not a continuous monitoring system and is not designed to detect heart attacks
    """

    @validate_date_param(field_name="before_date")
    @validate_date_param(field_name="after_date")
    @validate_pagination_params(max_limit=10)
    def get_irn_alerts_list(
        self,
        before_date: Optional[str] = None,
        after_date: Optional[str] = None,
        sort: SortDirection = SortDirection.DESCENDING,
        limit: int = 10,
        offset: int = 0,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """Returns a paginated list of Irregular Rhythm Notifications (IRN) alerts.

        This endpoint retrieves alerts generated when the user's device detected signs of
        possible atrial fibrillation (AFib). Only alerts that have been viewed by the user
        in their Fitbit app will be returned.

        API Reference: https://dev.fitbit.com/build/reference/web-api/irregular-rhythm-notifications/get-irn-alerts-list/

        Args:
            before_date: Return entries before this date (YYYY-MM-DD or 'today').
                        You can optionally include time in ISO 8601 format (YYYY-MM-DDThh:mm:ss).
            after_date: Return entries after this date (YYYY-MM-DD or 'today').
                       You can optionally include time in ISO 8601 format (YYYY-MM-DDThh:mm:ss).
            sort: Sort order - must use SortDirection.ASCENDING with after_date and
                 SortDirection.DESCENDING with before_date (default: DESCENDING)
            limit: Number of entries to return (max 10, default: 10)
            offset: Pagination offset (only 0 is supported by the Fitbit API)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Contains IRN alerts and pagination information for the requested period

        Raises:
            fitbit_client.exceptions.PaginationException: If neither before_date nor after_date is specified
            fitbit_client.exceptions.PaginationException: If offset is not 0
            fitbit_client.exceptions.PaginationException: If limit exceeds 10
            fitbit_client.exceptions.PaginationException: If sort direction doesn't match date parameter
                (must use ASCENDING with after_date, DESCENDING with before_date)
            fitbit_client.exceptions.InvalidDateException: If date format is invalid

        Note:
            - Either before_date or after_date must be specified, but not both
            - The offset parameter only supports 0; use the "next" URL in the pagination response
              to iterate through results
            - Tachogram data represents the time between heartbeats in milliseconds
            - The algorithm analyzes heart rate irregularity patterns during sleep
            - For research purposes only, not for clinical or diagnostic use
            - The alertTime is when the notification was generated, while detectedTime is
              when the irregular rhythm was detected (usually during sleep)
        """
        params: ParamDict = {"sort": sort.value, "limit": limit, "offset": offset}

        if before_date:
            params["beforeDate"] = before_date
        if after_date:
            params["afterDate"] = after_date

        result = self._make_request(
            "irn/alerts/list.json", params=params, user_id=user_id, debug=debug
        )
        return cast(JSONDict, result)

    def get_irn_profile(self, user_id: str = "-", debug: bool = False) -> JSONDict:
        """Returns the user's Irregular Rhythm Notifications (IRN) feature engagement status.

        This endpoint retrieves information about the user's enrollment status for the
        Irregular Rhythm Notifications feature, including whether they've completed the
        required onboarding process and when their data was last analyzed.

        API Reference: https://dev.fitbit.com/build/reference/web-api/irregular-rhythm-notifications/get-irn-profile/

        Args:
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: User's IRN feature engagement status including onboarding and enrollment information

        Raises:
            fitbit_client.exceptions.AuthorizationException: If missing the irregular_rhythm_notifications scope
            fitbit_client.exceptions.InvalidRequestException: If the user is not eligible for IRN

        Note:
            - "onboarded": True if the user has completed the IRN feature onboarding process
            - "enrolled": True if the user is actively enrolled and receiving notifications
            - "lastUpdated": Timestamp of when analyzable data was last synced to Fitbit servers
            - Users must complete an on-device onboarding flow to enable IRN
            - Enrollment can be paused/resumed by the user in their Fitbit app settings
            - Analyzing the data requires a compatible device, sufficient sleep data, and proper wear
        """
        result = self._make_request("irn/profile.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)
