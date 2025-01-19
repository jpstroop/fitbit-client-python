# resources/ecg.py
# Standard library imports
from typing import Any
from typing import Dict
from typing import Optional

# Local imports
from resources.base import BaseResource


class ECGResource(BaseResource):
    """
    Handles Fitbit Electrocardiogram (ECG) API endpoints for retrieving ECG readings.

    Note:
        The ECG API is for research use or investigational use only, and is not
        intended for clinical or diagnostic purposes.

    API Reference: https://dev.fitbit.com/build/reference/web-api/electrocardiogram/
    """

    def get_ecg_log_list(
        self,
        before_date: Optional[str] = None,
        after_date: Optional[str] = None,
        sort: str = "desc",
        limit: int = 10,
        offset: int = 0,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Get a list of user's ECG log entries before or after a given day.

        Args:
            before_date: Return entries before this date (YYYY-MM-ddTHH:mm:ss),
                        only YYYY-MM-dd is required
            after_date: Return entries after this date (YYYY-MM-ddTHH:mm:ss),
                       only YYYY-MM-dd is required
            sort: Sort order by date - use 'asc' with after_date, 'desc' with before_date
            limit: Number of entries to return (max 10)
            offset: Only 0 is supported
            user_id: Optional user ID, defaults to current user

        Note:
            Either before_date or after_date must be specified.
            The offset parameter only supports 0 and using other values may break your application.
            Use the pagination links in the response to iterate through results.

        Returns:
            Response contains ECG readings and pagination information. Each reading includes:
            start time, average heart rate, waveform samples, result classification, etc.

        Raises:
            ValueError: If neither before_date nor after_date is provided
            ValueError: If offset is not 0
            ValueError: If limit is greater than 10
        """
        if not before_date and not after_date:
            raise ValueError("Either before_date or after_date must be specified")

        if offset != 0:
            raise ValueError("Only offset=0 is supported")

        if limit > 10:
            raise ValueError("Maximum limit is 10")

        params = {"sort": sort, "limit": limit, "offset": offset}

        if before_date:
            params["beforeDate"] = before_date
        if after_date:
            params["afterDate"] = after_date

        return self._make_request("ecg/list.json", params=params, user_id=user_id)
