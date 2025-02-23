# fitbit_client/resources/electrocardiogram.py

# Standard library imports
from typing import Any
from typing import Dict
from typing import Optional

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import SortDirection
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.pagination_validation import validate_pagination_params


class ElectrocardiogramResource(BaseResource):
    """
    Handles Fitbit Electrocardiogram (ECG) API endpoints for retrieving ECG readings.

    Note:
        The ECG API is for research use or investigational use only, and is not
        intended for clinical or diagnostic purposes.

    API Reference: https://dev.fitbit.com/build/reference/web-api/electrocardiogram/
    """

    @validate_date_param(field_name="before_date")
    @validate_date_param(field_name="after_date")
    @validate_pagination_params(max_limit=10)
    def get_ecg_log_list(
        self,
        before_date: Optional[str] = None,
        after_date: Optional[str] = None,
        sort: SortDirection = SortDirection.DESCENDING,
        limit: int = 10,
        offset: int = 0,
        user_id: str = "-",
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Get a list of user's ECG log entries before or after a given day.

        API Reference: https://dev.fitbit.com/build/reference/web-api/electrocardiogram/get-ecg-log-list/

        Args:
            before_date: Return entries before this date (YYYY-MM-ddTHH:mm:ss),
                        only YYYY-MM-dd is required
            after_date: Return entries after this date (YYYY-MM-ddTHH:mm:ss),
                       only YYYY-MM-dd is required
            sort: Sort order - use 'asc' with after_date, 'desc' with before_date
            limit: Number of entries to return (max 10)
            offset: Only 0 is supported
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Note:
            Either before_date or after_date must be specified.
            The offset parameter only supports 0 and using other values may break your application.
            Use the pagination links in the response to iterate through results.

        Returns:
            Response contains ECG readings and pagination information. Each reading includes:
            start time, average heart rate, waveform samples, result classification, etc.

        Raises:
            PaginatonError: If neither before_date nor after_date is specified
            PaginatonError: If offset is not 0
            PaginatonError: If limit exceeds 10
            PaginatonError: If sort is not 'asc' or 'desc'
            PaginatonError: If sort direction doesn't match date parameter
            InvalidDateException: If date format is invalid
        """
        params = {"sort": sort.value, "limit": limit, "offset": offset}

        if before_date:
            params["beforeDate"] = before_date
        if after_date:
            params["afterDate"] = after_date

        return self._make_request("ecg/list.json", params=params, user_id=user_id, debug=debug)
