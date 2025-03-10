# fitbit_client/resources/spo2.py

# Standard library imports
from typing import cast

# Local imports
from fitbit_client.resources._base import BaseResource
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params
from fitbit_client.utils.types import JSONDict
from fitbit_client.utils.types import JSONList


class SpO2Resource(BaseResource):
    """Provides access to Fitbit SpO2 API for retrieving blood oxygen saturation data.

    This resource handles endpoints for retrieving blood oxygen saturation (SpO2) measurements
    taken during sleep. SpO2 data provides insights into breathing patterns and potential
    sleep-related breathing disturbances. Normal SpO2 levels during sleep typically range
    between 95-100%.

    API Reference: https://dev.fitbit.com/build/reference/web-api/spo2/

    Required Scopes:
      - oxygen_saturation: Required for all endpoints in this resource

    Note:
        SpO2 data represents measurements taken during the user's "main sleep" period
        (longest sleep period) and typically spans two dates since measurements are
        taken during overnight sleep. The data is usually associated with the date
        the user wakes up, not the date they went to sleep.

        SpO2 measurements require compatible Fitbit devices with SpO2 monitoring capability,
        such as certain Sense, Versa, and Charge models with the SpO2 clock face or app installed.

        The data is calculated on a 5-minute basis during sleep and requires at least 3 hours
        of quality sleep with minimal movement to generate readings.
    """

    @validate_date_param(field_name="date")
    def get_spo2_summary_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Returns SpO2 (blood oxygen saturation) summary data for a specific date.

        This endpoint provides daily summary statistics for blood oxygen saturation levels
        measured during sleep, including average, minimum, and maximum values. These metrics
        help monitor breathing quality during sleep.

        API Reference: https://dev.fitbit.com/build/reference/web-api/spo2/get-spo2-summary-by-date/

        Args:
            date: Date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: SpO2 summary with average, minimum and maximum blood oxygen percentage values

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            SpO2 data requires all of the following conditions:
            - Compatible device with SpO2 monitoring capability
            - SpO2 clock face or app installed and configured
            - At least 3 hours of quality sleep with minimal movement
            - Device sync after waking up
            - Up to 1 hour processing time after sync

            The date requested typically corresponds to the wake-up date, not the date
            when sleep began. For example, for overnight sleep from June 14 to June 15,
            the data would be associated with June 15.

            If no SpO2 data is available for the requested date, the API will return an empty
            response: {"dateTime": "2022-06-15"}
        """
        result = self._make_request(f"spo2/date/{date}.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    @validate_date_range_params()
    def get_spo2_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> JSONList:
        """Returns SpO2 (blood oxygen saturation) summary data for a date range.

        This endpoint provides daily summary statistics for blood oxygen saturation levels
        over a specified date range. It returns the same data as get_spo2_summary_by_date
        but for multiple days, allowing for trend analysis over time.

        API Reference: https://dev.fitbit.com/build/reference/web-api/spo2/get-spo2-summary-by-interval/

        Args:
            start_date: Start date in YYYY-MM-DD format or "today"
            end_date: End date in YYYY-MM-DD format or "today"
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONList: List of daily SpO2 summaries for the specified date range

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.InvalidDateRangeException: If start_date is after end_date
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Unlike many other Fitbit API endpoints, there is no maximum date range limit
            for this endpoint. However, requesting very large date ranges may impact
            performance and is generally not recommended.

            Days with no available SpO2 data will still be included in the response, but
            without the "value" field: {"dateTime": "2022-06-17"}

            SpO2 data requirements:
            - Compatible device with SpO2 monitoring capability
            - SpO2 clock face or app installed and configured
            - At least 3 hours of quality sleep with minimal movement
            - Device sync after waking up
            - Up to 1 hour processing time after sync
        """
        result = self._make_request(
            f"spo2/date/{start_date}/{end_date}.json", user_id=user_id, debug=debug
        )
        return cast(JSONList, result)
