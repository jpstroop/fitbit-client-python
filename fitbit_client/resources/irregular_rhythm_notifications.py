# fitbit_client/resources/irregular_rhythm_notifications.py

# Standard library imports
from typing import Any
from typing import Dict
from typing import Optional

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.utils.date_validation import validate_date_param


class IrregularRhythmNotificationsResource(BaseResource):
    """
    Handles Fitbit Irregular Rhythm Notifications (IRN) API endpoints for retrieving
    notifications and user engagement data.

    API Reference: https://dev.fitbit.com/build/reference/web-api/irregular-rhythm-notifications/

    Scope: rregular_rhythm_notifications

    Important:
        The IRN API is for research use or investigational use only, and is not intended
        for clinical or diagnostic purposes.

    Note:
        Only alerts that have been read by the user in the Fitbit app are accessible.
        IRN does not support subscription notifications (webhooks).
        Data is available after device sync and user interaction with notifications.
    """

    @validate_date_param(field_name="before_date")
    @validate_date_param(field_name="after_date")
    def get_irn_alerts_list(
        self,
        sort: str,
        limit: int = 10,
        offset: int = 0,
        before_date: Optional[str] = None,
        after_date: Optional[str] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Retrieves a paginated list of IRN alerts and their tachograms.

        API Reference: https://dev.fitbit.com/build/reference/web-api/irregular-rhythm-notifications/get-irn-alerts-list/

        Args:
            sort: Sort order of entries by date. Use 'asc' with after_date, 'desc' with before_date
            limit: Number of entries to return (max 10)
            offset: Pagination offset (only 0 is supported)
            before_date: Date in yyyy-MM-ddTHH:mm:ss format (at least yyyy-MM-dd required)
            after_date: Date in yyyy-MM-ddTHH:mm:ss format (at least yyyy-MM-dd required)
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Dictionary containing:
            - alerts: List of IRN alerts with detection times and heart rate data
            - pagination: Information for retrieving next/previous pages

        Raises:
            ValueError: If neither before_date nor after_date is specified
            ValueError: If offset is not 0
            ValueError: If limit exceeds 10
            ValueError: If sort is not 'asc' or 'desc'
            ValueError: If sort direction doesn't match date parameter
            InvalidDateException: If date format is invalid

        Note:
            Either before_date or after_date must be specified.
        """
        if offset != 0:
            raise ValueError("Only offset=0 is supported for IRN alerts pagination")

        if limit > 10:
            raise ValueError("Maximum limit is 10 entries")

        if not before_date and not after_date:
            raise ValueError("Either before_date or after_date must be specified")

        if sort not in ["asc", "desc"]:
            raise ValueError("Sort must be either 'asc' or 'desc'")

        if sort == "asc" and not after_date:
            raise ValueError("Must use after_date with ascending sort")

        if sort == "desc" and not before_date:
            raise ValueError("Must use before_date with descending sort")

        params = {"sort": sort, "limit": limit, "offset": offset}

        if before_date:
            params["beforeDate"] = before_date
        if after_date:
            params["afterDate"] = after_date

        return self._make_request(
            "irn/alerts/list.json", params=params, user_id=user_id, debug=debug
        )

    def get_irn_profile(self, user_id: str = "-", debug: bool = False) -> Dict[str, Any]:
        """
        Retrieves the user's IRN feature engagement status.

        API Reference: https://dev.fitbit.com/build/reference/web-api/irregular-rhythm-notifications/get-irn-profile/

        Args:
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Dictionary containing:
            - onboarded: Whether user has completed IRN feature onboarding
            - enrolled: Whether user is enrolled for IRN data processing
            - lastUpdated: Timestamp of last analyzable data sync
        """
        return self._make_request("irn/profile.json", user_id=user_id, debug=debug)
