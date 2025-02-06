# fitbit_client/resources/intraday.py

# Standard library imports
from logging import getLogger
from typing import Any
from typing import Dict
from typing import Optional

# Third party imports
from requests_oauthlib import OAuth2Session

# Local imports
from fitbit_client.exceptions import IntradayValidationException
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import IntradayDetailLevel
from fitbit_client.resources.constants import MaxRanges
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params


class IntradayResource(BaseResource):
    """
    Access to Fitbit Intraday API endpoints for detailed within-day data.

    OAuth 2.0 Application Type must be set to "Personal" to use Intraday data.
    All other application types require special approval from Fitbit.

    API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/
    """

    def __init__(self, oauth_session: OAuth2Session, locale: str, language: str) -> None:
        """Initialize the Intraday resource.

        Args:
            oauth_session: Authenticated OAuth2 session
            locale: Locale for the API requests
            language: Language for the API requests
        """
        super().__init__(oauth_session=oauth_session, locale=locale, language=language)
        self.logger = getLogger("fitbit_client.intraday")

    @validate_date_param(field_name="date")
    def get_azm_intraday_by_date(
        self,
        date: str,
        detail_level: IntradayDetailLevel,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Retrieves intraday active zone minutes time series data for a single date.

        Intraday support can extend the detail-level response to include 1min, 5min and 15min
        for Active Zone Minutes.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-azm-intraday-by-date/

        Args:
            date: The date in yyyy-MM-dd format or 'today'
            detail_level: Level of detail. Options: 1min, 5min, 15min
            start_time: Optional start time in HH:mm format
            end_time: Optional end time in HH:mm format
            user_id: User ID, defaults to current user
            debug: If True, prints the curl command instead of making the request

        Returns:
            Dict containing intraday active zone minutes data

        Raises:
            IntradayValidationException: If detail_level is invalid
            InvalidDateException: If date format is invalid
        """
        valid_levels = [
            IntradayDetailLevel.ONE_MINUTE,
            IntradayDetailLevel.FIVE_MINUTES,
            IntradayDetailLevel.FIFTEEN_MINUTES,
        ]
        if detail_level not in valid_levels:
            raise IntradayValidationException(
                message="Invalid detail level",
                field_name="detail_level",
                allowed_values=[l.value for l in valid_levels],
                resource_name="active zone minutes",
            )

        endpoint = f"activities/active-zone-minutes/date/{date}/1d/{detail_level.value}"
        if start_time and end_time:
            endpoint += f"/time/{start_time}/{end_time}"
        endpoint += ".json"

        return self._make_request(endpoint, user_id=user_id, debug=debug)

    @validate_date_range_params(
        max_days=MaxRanges.INTRADAY, resource_name="active zone minutes intraday"
    )
    def get_azm_intraday_by_interval(
        self,
        start_date: str,
        end_date: str,
        detail_level: IntradayDetailLevel,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Retrieves intraday active zone minutes time series data for a date range.

        Intraday support can extend the detail-level response to include 1min, 5min and 15min
        for Active Zone Minutes. Maximum date range is 24 hours.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-azm-intraday-by-interval/

        Args:
            start_date: Start date in yyyy-MM-dd format or 'today'
            end_date: End date in yyyy-MM-dd format or 'today'
            detail_level: Level of detail. Options: 1min, 5min, 15min
            start_time: Optional start time in HH:mm format
            end_time: Optional end time in HH:mm format
            user_id: User ID, defaults to current user
            debug: If True, prints the curl command instead of making the request

        Returns:
            Dict containing intraday active zone minutes data

        Raises:
            IntradayValidationException: If detail_level is invalid
            InvalidDateException: If date formats are invalid
            InvalidDateRangeException: If date range is invalid or exceeds 24 hours
        """
        valid_levels = [
            IntradayDetailLevel.ONE_MINUTE,
            IntradayDetailLevel.FIVE_MINUTES,
            IntradayDetailLevel.FIFTEEN_MINUTES,
        ]
        if detail_level not in valid_levels:
            raise IntradayValidationException(
                message="Invalid detail level",
                field_name="detail_level",
                allowed_values=[l.value for l in valid_levels],
                resource_name="active zone minutes",
            )

        endpoint = (
            f"activities/active-zone-minutes/date/{start_date}/{end_date}/{detail_level.value}"
        )
        if start_time and end_time:
            endpoint += f"/time/{start_time}/{end_time}"
        endpoint += ".json"

        return self._make_request(endpoint, user_id=user_id, debug=debug)

    @validate_date_param(field_name="date")
    def get_activity_intraday_by_date(
        self,
        date: str,
        resource_path: str,
        detail_level: IntradayDetailLevel,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Retrieves intraday activity time series data for a single date.

        Intraday support can extend the detail-level response to include 1min, 5min and 15min
        for Activity data.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-activity-intraday-by-date/

        Args:
            date: The date in yyyy-MM-dd format or 'today'
            resource_path: The resource type to fetch. Valid options:
                calories, distance, elevation, floors, steps, swimming-strokes
            detail_level: Level of detail. Options: 1min, 5min, 15min
            start_time: Optional start time in HH:mm format
            end_time: Optional end time in HH:mm format
            user_id: User ID, defaults to current user
            debug: If True, prints the curl command instead of making the request

        Returns:
            Dict containing intraday activity data for the specified resource

        Raises:
            IntradayValidationException: If detail_level or resource_path is invalid
            InvalidDateException: If date format is invalid

        Note:
            Activity intraday data cannot be retrieved for more than a 24 hour period.
            Personal applications automatically have access to intraday data.
            Other application types require special approval from Fitbit.
        """
        valid_resources = {
            "calories",
            "distance",
            "elevation",
            "floors",
            "steps",
            "swimming-strokes",
        }
        if resource_path not in valid_resources:
            raise IntradayValidationException(
                message="Invalid resource path",
                field_name="resource_path",
                allowed_values=sorted(list(valid_resources)),
                resource_name="activity",
            )

        valid_levels = [
            IntradayDetailLevel.ONE_MINUTE,
            IntradayDetailLevel.FIVE_MINUTES,
            IntradayDetailLevel.FIFTEEN_MINUTES,
        ]
        if detail_level not in valid_levels:
            raise IntradayValidationException(
                message="Invalid detail level",
                field_name="detail_level",
                allowed_values=[l.value for l in valid_levels],
                resource_name="activity",
            )

        endpoint = f"activities/{resource_path}/date/{date}/1d/{detail_level.value}"
        if start_time and end_time:
            endpoint += f"/time/{start_time}/{end_time}"
        endpoint += ".json"

        return self._make_request(endpoint, user_id=user_id, debug=debug)

    @validate_date_range_params(max_days=MaxRanges.INTRADAY, resource_name="activity intraday")
    def get_activity_intraday_by_interval(
        self,
        start_date: str,
        end_date: str,
        resource_path: str,
        detail_level: IntradayDetailLevel,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Retrieves intraday activity time series data for a date range.

        Intraday support can extend the detail-level response to include 1min, 5min and 15min
        for Activity data.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-activity-intraday-by-interval/

        Args:
            start_date: Start date in yyyy-MM-dd format or 'today'
            end_date: End date in yyyy-MM-dd format or 'today'
            resource_path: The resource type to fetch. Valid options:
                calories, distance, elevation, floors, steps, swimming-strokes
            detail_level: Level of detail. Options: 1min, 5min, 15min
            start_time: Optional start time in HH:mm format
            end_time: Optional end time in HH:mm format
            user_id: User ID, defaults to current user
            debug: If True, prints the curl command instead of making the request

        Returns:
            Dict containing intraday activity data for the specified resource

        Raises:
            IntradayValidationException: If detail_level or resource_path is invalid
            InvalidDateException: If date formats are invalid
            InvalidDateRangeException: If date range is invalid or exceeds 24 hours

        Note:
            Activity intraday data cannot be retrieved for more than a 24 hour period.
            Personal applications automatically have access to intraday data.
            Other application types require special approval from Fitbit.
        """
        valid_resources = {
            "calories",
            "distance",
            "elevation",
            "floors",
            "steps",
            "swimming-strokes",
        }
        if resource_path not in valid_resources:
            raise IntradayValidationException(
                message="Invalid resource path",
                field_name="resource_path",
                allowed_values=sorted(list(valid_resources)),
                resource_name="activity",
            )

        valid_levels = [
            IntradayDetailLevel.ONE_MINUTE,
            IntradayDetailLevel.FIVE_MINUTES,
            IntradayDetailLevel.FIFTEEN_MINUTES,
        ]
        if detail_level not in IntradayDetailLevel:
            raise IntradayValidationException(
                message="Invalid detail level",
                field_name="detail_level",
                allowed_values=[l.value for l in valid_levels],
                resource_name="activity",
            )

        endpoint = f"activities/{resource_path}/date/{start_date}/{end_date}/{detail_level.value}"
        if start_time and end_time:
            endpoint += f"/time/{start_time}/{end_time}"
        endpoint += ".json"

        return self._make_request(endpoint, user_id=user_id, debug=debug)

    @validate_date_param(field_name="date")
    def get_breathing_rate_intraday_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieves intraday breathing rate data for a single date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-br-intraday-by-date/

        Args:
            date: The date in yyyy-MM-dd format or 'today'
            start_time: Optional start time in HH:mm format
            end_time: Optional end time in HH:mm format
            user_id: User ID, defaults to current user
            debug: If True, prints the curl command instead of making the request

        Returns:
            Dict containing intraday breathing rate data

        Raises:
            InvalidDateException: If date format is invalid
        """
        endpoint = f"br/date/{date}/all.json"
        return self._make_request(endpoint, user_id=user_id, debug=debug)

    @validate_date_range_params(max_days=30, resource_name="breathing rate intraday")
    def get_breathing_rate_intraday_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieves intraday breathing rate data for a date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-br-intraday-by-interval/

        Args:
            start_date: Start date in yyyy-MM-dd format or 'today'
            end_date: End date in yyyy-MM-dd format or 'today'
            user_id: User ID, defaults to current user
            debug: If True, prints the curl command instead of making the request

        Returns:
            Dict containing intraday breathing rate data

        Raises:
            IntradayValidationException: If detail_level is invalid
            InvalidDateException: If date formats are invalid
            InvalidDateRangeException: If date range is invalid or exceeds 30 days
        """

        endpoint = f"br/date/{start_date}/{end_date}/all.json"
        return self._make_request(endpoint, user_id=user_id, debug=debug)

    @validate_date_param(field_name="date")
    def get_heartrate_intraday_by_date(
        self,
        date: str,
        detail_level: IntradayDetailLevel,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Retrieves intraday heart rate time series data for a single date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-heartrate-intraday-by-date/

        Args:
            date: The date in yyyy-MM-dd format or 'today'
            detail_level: Level of detail
            start_time: Optional start time in HH:mm format
            end_time: Optional end time in HH:mm format
            user_id: User ID, defaults to current user
            debug: If True, prints the curl command instead of making the request

        Returns:
            Dict containing intraday heart rate data

        Raises:
            IntradayValidationException: If detail_level is invalid
            InvalidDateException: If date format is invalid
        """
        if detail_level not in IntradayDetailLevel:
            raise IntradayValidationException(
                message="Invalid detail level",
                field_name="detail_level",
                allowed_values=[l.value for l in IntradayDetailLevel],
                resource_name="heart rate",
            )

        endpoint = f"activities/heart/date/{date}/1d/{detail_level.value}"
        if start_time and end_time:
            endpoint += f"/time/{start_time}/{end_time}"
        endpoint += ".json"

        return self._make_request(endpoint, user_id=user_id, debug=debug)

    @validate_date_range_params()
    def get_heartrate_intraday_by_interval(
        self,
        start_date: str,
        end_date: str,
        detail_level: IntradayDetailLevel = IntradayDetailLevel.ONE_MINUTE,
        user_id: str = "-",
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Retrieves intraday heart rate time series data for a date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-heartrate-intraday-by-interval/

        Args:
            start_date: Start date in yyyy-MM-dd format or 'today'
            end_date: End date in yyyy-MM-dd format or 'today'
            detail_level: Level of detail. Options: 1sec, 1min
            user_id: User ID, defaults to current user
            debug: If True, prints the curl command instead of making the request

        Returns:
            Dict containing intraday heart rate data

        Raises:
            IntradayValidationException: If detail_level is invalid
            InvalidDateException: If date formats are invalid
            InvalidDateRangeException: If date range is invalid
        """
        valid_levels = [IntradayDetailLevel.ONE_SECOND, IntradayDetailLevel.ONE_MINUTE]
        if detail_level not in valid_levels:
            raise IntradayValidationException(
                message="Invalid detail level",
                field_name="detail_level",
                allowed_values=[l.value for l in valid_levels],
                resource_name="heart rate",
            )

        endpoint = f"activities/heart/date/{start_date}/{end_date}/{detail_level.value}.json"
        return self._make_request(endpoint, user_id=user_id, debug=debug)

    @validate_date_param(field_name="date")
    def get_hrv_intraday_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieves intraday heart rate variability (HRV) data for a single date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-hrv-intraday-by-date/

        Args:
            date: The date in yyyy-MM-dd format or 'today'
            user_id: User ID, defaults to current user
            debug: If True, prints the curl command instead of making the request

        Returns:
            Dict containing intraday HRV data including rmssd, coverage, hf, and lf measurements

        Raises:
            InvalidDateException: If date format is invalid

        Note:
            * HRV data applies specifically to a user's "main sleep" period
            * Data is returned every 5 minutes during sleep
            * Values usually reflect sleep that began the previous day
            * Requires:
                - Health Metrics tile enabled in mobile app
                - Minimum 3 hours of sleep
                - Sleep stages log creation
                - Device compatibility (see Fitbit Product page)
            * Processing takes ~15 minutes after device sync
        """
        endpoint = f"hrv/date/{date}/all.json"
        return self._make_request(endpoint, user_id=user_id, debug=debug)

    @validate_date_range_params(max_days=30, resource_name="heart rate variability intraday")
    def get_hrv_intraday_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieves intraday heart rate variability (HRV) data for a date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-hrv-intraday-by-interval/

        Args:
            start_date: Start date in yyyy-MM-dd format or 'today'
            end_date: End date in yyyy-MM-dd format or 'today'
            user_id: User ID, defaults to current user
            debug: If True, prints the curl command instead of making the request

        Returns:
            Dict containing intraday HRV data including rmssd, coverage, hf, and lf measurements

        Raises:
            InvalidDateException: If date formats are invalid
            InvalidDateRangeException: If date range is invalid or exceeds 30 days

        Note:
            * HRV data applies specifically to a user's "main sleep" period
            * Data is returned every 5 minutes during sleep
            * Values usually reflect sleep that began the previous day
            * Maximum date range is 30 days
            * Requires:
                - Health Metrics tile enabled in mobile app
                - Minimum 3 hours of sleep
                - Sleep stages log creation
                - Device compatibility (see Fitbit Product page)
            * Processing takes ~15 minutes after device sync
        """
        endpoint = f"hrv/date/{start_date}/{end_date}/all.json"
        return self._make_request(endpoint, user_id=user_id, debug=debug)

    @validate_date_param(field_name="date")
    def get_spo2_intraday_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieves intraday SpO2 (blood oxygen saturation) data for a single date.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-spo2-intraday-by-date/

        Args:
            date: The date in yyyy-MM-dd format or 'today'
            user_id: User ID, defaults to current user
            debug: If True, prints the curl command instead of making the request

        Returns:
            Dict containing intraday SpO2 percentage values with timestamps

        Raises:
            InvalidDateException: If date format is invalid

        Note:
            * SpO2 data applies specifically to a user's "main sleep" period
            * Values calculated on a 5-minute exponentially-moving average
            * Values usually reflect sleep that began the previous day
            * Requires:
                - Minimum 3 hours of quality sleep
                - Limited physical movement
                - Device compatibility (see Fitbit Product page)
            * Processing takes up to 1 hour after device sync
        """
        endpoint = f"spo2/date/{date}/all.json"
        return self._make_request(endpoint, user_id=user_id, debug=debug)

    @validate_date_range_params(max_days=30, resource_name="spo2 intraday")
    def get_spo2_intraday_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieves intraday SpO2 (blood oxygen saturation) data for a date range.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-spo2-intraday-by-interval/

        Args:
            start_date: Start date in yyyy-MM-dd format or 'today'
            end_date: End date in yyyy-MM-dd format or 'today'
            user_id: User ID, defaults to current user
            debug: If True, prints the curl command instead of making the request

        Returns:
            Dict containing intraday SpO2 percentage values with timestamps

        Raises:
            InvalidDateException: If date formats are invalid
            InvalidDateRangeException: If date range is invalid or exceeds 30 days

        Note:
            * SpO2 data applies specifically to a user's "main sleep" period
            * Values calculated on a 5-minute exponentially-moving average
            * Values usually reflect sleep that began the previous day
            * Maximum date range is 30 days
            * Requires:
                - Minimum 3 hours of quality sleep
                - Limited physical movement
                - Device compatibility (see Fitbit Product page)
            * Processing takes up to 1 hour after device sync
        """
        endpoint = f"spo2/date/{start_date}/{end_date}/all.json"
        return self._make_request(endpoint, user_id=user_id, debug=debug)
