# resources/activezone.py
# Standard library imports
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

# Third party imports
from resources.base import BaseResource
from resources.constants import Period


class ActiveZoneResource(BaseResource):
    """
    Handles Fitbit Active Zone Minutes (AZM) API endpoints for retrieving user's
    heart-pumping activity data throughout the day.

    API Reference: https://dev.fitbit.com/build/reference/web-api/active-zone-minutes-timeseries/
    """

    def get_azm_by_date(self, date: str, period: Period, user_id: str = "-") -> Dict[str, Any]:
        """
        Get Active Zone Minutes time series data for a period starting from the specified date.

        Args:
            date: The end date of the period in yyyy-MM-dd format or 'today'
            period: The range for which data will be returned
                   Supported values: 1d, 7d, 30d, 1w, 1m, 3m, 6m, 1y
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.

        Returns:
            Daily AZM data for the specified period including:
            - Total active zone minutes
            - Fat burn zone minutes (1 minute = 1 AZM)
            - Cardio zone minutes (1 minute = 2 AZM)
            - Peak zone minutes (1 minute = 2 AZM)
        """
        if not isinstance(period, Period):
            raise ValueError(f"Period must be a valid Period enum value. Got: {period}")

        return self._make_request(
            f"activities/active-zone-minutes/date/{date}/{period.value}.json", user_id=user_id
        )

    def get_azm_by_date_range(
        self, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """
        Get Active Zone Minutes time series data for a specified date range.

        Args:
            start_date: The start date in yyyy-MM-dd format or 'today'
            end_date: The end date in yyyy-MM-dd format or 'today'
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.

        Returns:
            Daily AZM data for each date in the range including:
            - Total active zone minutes
            - Fat burn zone minutes (1 minute = 1 AZM)
            - Cardio zone minutes (1 minute = 2 AZM)
            - Peak zone minutes (1 minute = 2 AZM)

        Note:
            Maximum date range is 1095 days (approximately 3 years)
        """
        return self._make_request(
            f"activities/active-zone-minutes/date/{start_date}/{end_date}.json", user_id=user_id
        )
