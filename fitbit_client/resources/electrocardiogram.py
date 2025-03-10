# fitbit_client/resources/electrocardiogram.py

# Standard library imports
from typing import Any
from typing import Dict
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union
from typing import cast

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import SortDirection
from fitbit_client.resources.pagination import create_paginated_iterator
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.pagination_validation import validate_pagination_params
from fitbit_client.utils.types import JSONDict
from fitbit_client.utils.types import ParamDict

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    # Local imports - only imported during type checking
    # Local imports
    from fitbit_client.resources.pagination import PaginatedIterator


class ElectrocardiogramResource(BaseResource):
    """Provides access to Fitbit Electrocardiogram (ECG) API for retrieving heart rhythm assessments.

    This resource handles endpoints for retrieving ECG readings taken using compatible Fitbit devices.
    ECG (electrocardiogram) readings can help detect signs of atrial fibrillation (AFib),
    which is an irregular heart rhythm that requires medical attention.

    API Reference: https://dev.fitbit.com/build/reference/web-api/electrocardiogram/

    Required Scopes:
        - electrocardiogram (for all ECG endpoints)

    Note:
        The ECG API is for research use or investigational use only, and is not
        intended for clinical or diagnostic purposes. ECG results do not replace
        traditional diagnosis methods and should not be interpreted as medical advice.

        ECG readings require a compatible Fitbit device (e.g., Fitbit Sense or newer)
        and proper finger placement during measurement. The measurement process takes
        approximately 30 seconds.

        ECG results are classified into several categories:
        - Normal sinus rhythm: No signs of atrial fibrillation detected
        - Atrial fibrillation: Irregular rhythm that may indicate AFib
        - Inconclusive: Result could not be classified
        - Inconclusive (High heart rate): Heart rate was too high for assessment
        - Inconclusive (Low heart rate): Heart rate was too low for assessment
        - Inconclusive (Poor reading): Signal quality was insufficient for assessment
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
        as_iterator: bool = False,
    ) -> Union[JSONDict, "PaginatedIterator"]:
        """Returns a list of user's ECG log entries before or after a given day.

        API Reference: https://dev.fitbit.com/build/reference/web-api/electrocardiogram/get-ecg-log-list/

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
            as_iterator: If True, returns a PaginatedIterator instead of the raw response (default: False)

        Returns:
            If as_iterator=False (default):
                JSONDict: ECG readings with classifications and pagination information
            If as_iterator=True:
                PaginatedIterator: An iterator that yields each page of ECG readings

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

            When using as_iterator=True, you can iterate through all pages like this:
            ```python
            for page in client.get_ecg_log_list(before_date="2025-01-01", as_iterator=True):
                for reading in page["ecgReadings"]:
                    print(reading["startTime"])
            ```

            - waveformSamples contains the actual ECG data points (300 samples per second)
            - resultClassification indicates the assessment outcome (normal, afib, inconclusive)
            - For research purposes only, not for clinical or diagnostic use
        """
        params: ParamDict = {"sort": sort.value, "limit": limit, "offset": offset}

        if before_date:
            params["beforeDate"] = before_date
        if after_date:
            params["afterDate"] = after_date

        endpoint = "ecg/list.json"
        result = self._make_request(endpoint, params=params, user_id=user_id, debug=debug)

        # If debug mode is enabled, result will be None
        if debug or result is None:
            return cast(JSONDict, result)

        # Return as iterator if requested
        if as_iterator:
            return create_paginated_iterator(
                response=cast(JSONDict, result),
                resource=self,
                endpoint=endpoint,
                method_params=params,
                debug=debug,
            )

        return cast(JSONDict, result)
