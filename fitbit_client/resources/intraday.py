# fitbit_client/resources/intraday.py

# Standard library imports
from typing import Optional
from typing import cast

# Local imports
from fitbit_client.exceptions import IntradayValidationException
from fitbit_client.resources._base import BaseResource
from fitbit_client.resources._constants import IntradayDetailLevel
from fitbit_client.resources._constants import MaxRanges
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range_params
from fitbit_client.utils.types import JSONDict


class IntradayResource(BaseResource):
    """Provides access to Fitbit Intraday API for retrieving detailed within-day time series data.

    This resource handles endpoints for retrieving minute-by-minute or second-by-second data
    for various metrics including activity (steps, calories), heart rate, SpO2, breathing rate,
    heart rate variability (HRV), and active zone minutes. The intraday data provides much more
    granular insights than the daily summary endpoints.

    API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/

    Required Scopes:
      - activity: For activity-related intraday data
      - heartrate: For heart rate intraday data
      - respiratory_rate: For breathing rate intraday data
      - oxygen_saturation: For SpO2 intraday data
      - cardio_fitness: For heart rate variability intraday data

    Note:
        OAuth 2.0 Application Type must be set to "Personal" to use intraday data.
        All other application types require special approval from Fitbit.

        Intraday data is much more detailed than daily summaries and has strict
        limitations on date ranges (usually 24 hours or 30 days maximum).

        Different metrics support different granularity levels. For example,
        heart rate data is available at 1-second or 1-minute intervals, while
        activity data is available at 1-minute, 5-minute, or 15-minute intervals.
    """

    @validate_date_param(field_name="date")
    def get_azm_intraday_by_date(
        self,
        date: str,
        detail_level: IntradayDetailLevel,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """Retrieves intraday active zone minutes time series data for a single date.

        This endpoint provides minute-by-minute active zone minutes data, showing the
        intensity of activity throughout the day. Active Zone Minutes are earned when
        in the fat burn, cardio, or peak heart rate zones.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-azm-intraday-by-date/

        Args:
            date: The date in YYYY-MM-DD format or 'today'
            detail_level: Level of detail (ONE_MINUTE, FIVE_MINUTES, or FIFTEEN_MINUTES)
            start_time: Optional start time in HH:mm format to limit the time window
            end_time: Optional end time in HH:mm format to limit the time window
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Active zone minutes data containing daily summary and intraday time series

        Raises:
            fitbit_client.exceptions.IntradayValidationException: If detail_level is invalid
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Active Zone Minutes measure time spent in heart rate zones that count toward
            your weekly goals. Different detail levels change the granularity of the data:
            - ONE_MINUTE (1min): Shows minute-by-minute values
            - FIVE_MINUTES (5min): Shows values averaged over 5-minute intervals
            - FIFTEEN_MINUTES (15min): Shows values averaged over 15-minute intervals

            The "activities-active-zone-minutes" section contains daily summary data,
            while the "intraday" section contains the detailed time-specific data.

            AZM values are categorized by intensity zones:
            - Fat Burn: Moderate intensity (1 Active Zone Minute per minute)
            - Cardio: High intensity (2 Active Zone Minutes per minute)
            - Peak: Very high intensity (2 Active Zone Minutes per minute)

            Personal applications automatically have access to intraday data.
            Other application types require special approval from Fitbit.
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

        return cast(JSONDict, self._make_request(endpoint, user_id=user_id, debug=debug))

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
    ) -> JSONDict:
        """Retrieves intraday active zone minutes time series data for a date range.

        This endpoint provides minute-by-minute active zone minutes data across multiple days,
        showing the intensity of activity throughout the specified period. The maximum date
        range is limited to 24 hours.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-azm-intraday-by-interval/

        Args:
            start_date: Start date in YYYY-MM-DD format or 'today'
            end_date: End date in YYYY-MM-DD format or 'today'
            detail_level: Level of detail (ONE_MINUTE, FIVE_MINUTES, or FIFTEEN_MINUTES)
            start_time: Optional start time in HH:mm format to limit the time window
            end_time: Optional end time in HH:mm format to limit the time window
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Active zone minutes data containing daily summaries and intraday time series

        Raises:
            fitbit_client.exceptions.IntradayValidationException: If detail_level is invalid
            fitbit_client.exceptions.InvalidDateException: If date formats are invalid
            fitbit_client.exceptions.InvalidDateRangeException: If date range is invalid or exceeds 24 hours
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Important limitations:
            - Maximum date range is 24 hours (1 day), even if start_date and end_date differ by more
            - For longer periods, make multiple requests with consecutive date ranges

            The different detail levels change the granularity of the data:
            - ONE_MINUTE (1min): Shows minute-by-minute values
            - FIVE_MINUTES (5min): Shows values averaged over 5-minute intervals
            - FIFTEEN_MINUTES (15min): Shows values averaged over 15-minute intervals

            The time window parameters (start_time/end_time) can be useful to limit the
            amount of data returned, especially when you're only interested in activity
            during specific hours of the day.

            Personal applications automatically have access to intraday data.
            Other application types require special approval from Fitbit.
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

        return cast(JSONDict, self._make_request(endpoint, user_id=user_id, debug=debug))

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
    ) -> JSONDict:
        """Retrieves intraday activity time series data for a single date.

        This endpoint provides detailed activity metrics (steps, calories, distance, etc.)
        at regular intervals throughout the day, allowing analysis of activity patterns
        with much greater precision than daily summaries.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-activity-intraday-by-date/

        Args:
            date: The date in YYYY-MM-DD format or 'today'
            resource_path: The activity metric to fetch (e.g., "steps", "calories", "distance")
            detail_level: Level of detail (ONE_MINUTE, FIVE_MINUTES, or FIFTEEN_MINUTES)
            start_time: Optional start time in HH:mm format to limit the time window
            end_time: Optional end time in HH:mm format to limit the time window
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Activity data with daily summary and intraday time series for the specified metric

        Raises:
            fitbit_client.exceptions.IntradayValidationException: If detail_level or resource_path is invalid
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Valid resource_path options:
            - "calories": Calories burned per interval
            - "steps": Step count per interval
            - "distance": Distance covered per interval (in miles or kilometers)
            - "floors": Floors climbed per interval
            - "elevation": Elevation change per interval (in feet or meters)
            - "swimming-strokes": Swimming strokes per interval

            Different detail levels change the granularity of the data:
            - ONE_MINUTE (1min): Shows minute-by-minute values
            - FIVE_MINUTES (5min): Shows values averaged or summed over 5-minute intervals
            - FIFTEEN_MINUTES (15min): Shows values averaged or summed over 15-minute intervals

            The response format changes based on the resource_path, with the appropriate
            field names ("activities-steps", "activities-calories", etc.), but the
            overall structure remains the same.

            Activity units are based on the user's profile settings:
            - Imperial: miles, feet
            - Metric: kilometers, meters

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

        return cast(JSONDict, self._make_request(endpoint, user_id=user_id, debug=debug))

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
    ) -> JSONDict:
        """Retrieves intraday activity time series data for a date range.

        This endpoint provides detailed activity metrics across multiple days, with the
        same level of granularity as the single-date endpoint. The maximum date range
        is limited to 24 hours to keep response sizes manageable.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-activity-intraday-by-interval/

        Args:
            start_date: Start date in YYYY-MM-DD format or 'today'
            end_date: End date in YYYY-MM-DD format or 'today'
            resource_path: The activity metric to fetch (e.g., "steps", "calories", "distance")
            detail_level: Level of detail (ONE_MINUTE, FIVE_MINUTES, or FIFTEEN_MINUTES)
            start_time: Optional start time in HH:mm format to limit the time window
            end_time: Optional end time in HH:mm format to limit the time window
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Activity data with daily summaries and intraday time series for the specified metric

        Raises:
            fitbit_client.exceptions.IntradayValidationException: If detail_level or resource_path is invalid
            fitbit_client.exceptions.InvalidDateException: If date formats are invalid
            fitbit_client.exceptions.InvalidDateRangeException: If date range is invalid or exceeds 24 hours
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Important limitations:
            - Maximum date range is 24 hours (1 day), even if start_date and end_date differ by more
            - For longer periods, make multiple requests with consecutive date ranges

            Valid resource_path options:
            - "calories": Calories burned per interval
            - "steps": Step count per interval
            - "distance": Distance covered per interval (in miles or kilometers)
            - "floors": Floors climbed per interval
            - "elevation": Elevation change per interval (in feet or meters)
            - "swimming-strokes": Swimming strokes per interval

            Different detail levels change the granularity of the data:
            - ONE_MINUTE (1min): Shows minute-by-minute values
            - FIVE_MINUTES (5min): Shows values averaged or summed over 5-minute intervals
            - FIFTEEN_MINUTES (15min): Shows values averaged or summed over 15-minute intervals

            The response format will differ based on the resource_path, but the overall
            structure remains the same.

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

        endpoint = f"activities/{resource_path}/date/{start_date}/{end_date}/{detail_level.value}"
        if start_time and end_time:
            endpoint += f"/time/{start_time}/{end_time}"
        endpoint += ".json"

        return cast(JSONDict, self._make_request(endpoint, user_id=user_id, debug=debug))

    @validate_date_param(field_name="date")
    def get_breathing_rate_intraday_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Retrieves intraday breathing rate data for a single date.

        This endpoint returns detailed breathing rate measurements recorded during sleep.
        Breathing rate data provides insights into respiratory health, sleep quality,
        and potential health issues.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-br-intraday-by-date/

        Args:
            date: The date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Breathing rate data including summary and detailed measurements during sleep

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            Breathing rate data is collected during sleep periods and is measured in
            breaths per minute (BPM). Typical adult resting breathing rates range from
            12-20 breaths per minute.

            The data is collected in approximately 15-minute intervals during sleep.
            Each measurement includes a confidence level indicating the reliability
            of the reading.

            Different sleep stages normally have different breathing rates:
            - Deep sleep: Typically slower, more regular breathing
            - REM sleep: Variable breathing rate, may be faster or more irregular

            Breathing rate data requires a compatible Fitbit device with the appropriate
            sensors and the Health Metrics Dashboard enabled in the Fitbit app.

            This data is associated with the date the sleep ends, even if the sleep
            session began on the previous day.
        """
        endpoint = f"br/date/{date}/all.json"
        return cast(JSONDict, self._make_request(endpoint, user_id=user_id, debug=debug))

    @validate_date_range_params(max_days=30, resource_name="breathing rate intraday")
    def get_breathing_rate_intraday_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Retrieves intraday breathing rate data for a date range.

        This endpoint returns detailed breathing rate measurements recorded during sleep
        across multiple days, up to a maximum range of 30 days.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-br-intraday-by-interval/

        Args:
            start_date: Start date in YYYY-MM-DD format or 'today'
            end_date: End date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Breathing rate data including daily summaries and detailed measurements during sleep

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date formats are invalid
            fitbit_client.exceptions.InvalidDateRangeException: If date range is invalid or exceeds 30 days
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            The maximum date range for this endpoint is 30 days. For longer historical
            periods, you will need to make multiple requests with different date ranges.

            Breathing rate data is collected during sleep periods and is measured in
            breaths per minute (BPM). The returned data includes:
            - Daily summary values for different sleep stages
            - Detailed intraday measurements throughout each sleep session

            Each day's data is associated with the date the sleep ends, even if the sleep
            session began on the previous day.

            This endpoint requires the "respiratory_rate" OAuth scope and a compatible
            Fitbit device with the appropriate sensors and the Health Metrics Dashboard
            enabled in the Fitbit app.

            Analyzing breathing rate trends over time can provide insights into:
            - Sleep quality and patterns
            - Recovery from exercise or illness
            - Potential respiratory issues
        """

        endpoint = f"br/date/{start_date}/{end_date}/all.json"
        return cast(JSONDict, self._make_request(endpoint, user_id=user_id, debug=debug))

    @validate_date_param(field_name="date")
    def get_heartrate_intraday_by_date(
        self,
        date: str,
        detail_level: IntradayDetailLevel,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """Returns detailed heart rate data at minute or second intervals for a single date.

        This endpoint retrieves heart rate measurements at the specified granularity (detail level)
        for a specific date. It can optionally be limited to a specific time window within the day.
        This provides much more detailed heart rate data than the daily summary endpoints.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-heartrate-intraday-by-date/

        Args:
            date: The date in YYYY-MM-DD format or 'today'
            detail_level: Level of detail (IntradayDetailLevel.ONE_SECOND or IntradayDetailLevel.ONE_MINUTE)
            start_time: Optional start time in HH:mm format to limit the time window
            end_time: Optional end time in HH:mm format to limit the time window
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Heart rate data including daily summary and detailed time series

        Raises:
            fitbit_client.exceptions.IntradayValidationException: If detail_level is invalid
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            The "activities-heart" section contains the same data as the daily heart rate summary.
            The "activities-heart-intraday" section contains the detailed, minute-by-minute or
            second-by-second heart rate measurements.

            For one-second detail level (1sec), the dataset can be very large, potentially
            containing up to 86,400 data points for a full day. For applications handling
            large volumes of data, consider using time windows (start_time/end_time)
            to limit the response size.

            Personal applications automatically have access to intraday data.
            Other application types require special approval from Fitbit.
        """
        valid_levels = list(IntradayDetailLevel)
        if detail_level not in valid_levels:
            raise IntradayValidationException(
                message="Invalid detail level",
                field_name="detail_level",
                allowed_values=[l.value for l in valid_levels],
                resource_name="heart rate",
            )

        endpoint = f"activities/heart/date/{date}/1d/{detail_level.value}"
        if start_time and end_time:
            endpoint += f"/time/{start_time}/{end_time}"
        endpoint += ".json"

        return cast(JSONDict, self._make_request(endpoint, user_id=user_id, debug=debug))

    @validate_date_range_params()
    def get_heartrate_intraday_by_interval(
        self,
        start_date: str,
        end_date: str,
        detail_level: IntradayDetailLevel = IntradayDetailLevel.ONE_MINUTE,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """Retrieves intraday heart rate time series data for a date range.

        This endpoint provides second-by-second or minute-by-minute heart rate measurements
        across multiple days. This allows for detailed analysis of heart rate patterns
        and trends over extended periods.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-heartrate-intraday-by-interval/

        Args:
            start_date: Start date in YYYY-MM-DD format or 'today'
            end_date: End date in YYYY-MM-DD format or 'today'
            detail_level: Level of detail (ONE_SECOND or ONE_MINUTE, default: ONE_MINUTE)
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Heart rate data including daily summaries and detailed time series

        Raises:
            fitbit_client.exceptions.IntradayValidationException: If detail_level is invalid
            fitbit_client.exceptions.InvalidDateException: If date formats are invalid
            fitbit_client.exceptions.InvalidDateRangeException: If date range is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            This endpoint supports two levels of detail:
            - ONE_SECOND (1sec): Heart rate readings every second, providing maximum granularity
            - ONE_MINUTE (1min): Heart rate readings every minute, for more manageable data size

            For ONE_SECOND detail level, the response can be extremely large for longer
            date ranges, potentially containing up to 86,400 data points per day. Consider
            using ONE_MINUTE detail level unless you specifically need second-level detail.

            Unlike most other intraday endpoints, there is no explicit maximum date range
            for this endpoint. However, requesting too much data at once can result in
            timeouts or very large responses. For best performance, limit requests to
            a few days at a time, especially with ONE_SECOND detail level.

            Heart rate data is recorded continuously when a compatible Fitbit device
            is worn, with gaps during times when the device is not worn or cannot
            get a reliable reading.

            Personal applications automatically have access to intraday data.
            Other application types require special approval from Fitbit.
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
        return cast(JSONDict, self._make_request(endpoint, user_id=user_id, debug=debug))

    @validate_date_param(field_name="date")
    def get_hrv_intraday_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Retrieves intraday heart rate variability (HRV) data for a single date.

        This endpoint returns detailed heart rate variability measurements taken during sleep.
        HRV is a key indicator of autonomic nervous system health, stress levels, and recovery.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-hrv-intraday-by-date/

        Args:
            date: The date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Heart rate variability data including daily summary and detailed measurements

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            HRV data is collected specifically during the user's "main sleep" period
            (typically the longest sleep of the day). Key information:

            - RMSSD (Root Mean Square of Successive Differences): The primary HRV
              metric measured in milliseconds. Higher values typically indicate better
              recovery and lower stress levels. Normal adult ranges vary widely from
              approximately 20-100ms.

            - Data is collected in 5-minute intervals during sleep.

            - HF (High Frequency) power: Associated with parasympathetic nervous system
              activity (rest and recovery).

            - LF (Low Frequency) power: Influenced by both sympathetic (stress response)
              and parasympathetic nervous systems.

            - Coverage: Indicates the quality of the data collection during each interval.

            Requirements for HRV data collection:
            - Health Metrics tile enabled in the Fitbit mobile app
            - Minimum 3 hours of sleep
            - Sleep stages log creation (depends on device having heart rate sensor)
            - Compatible Fitbit device

            Data processing takes approximately 15 minutes after device sync.
            The date represents when the sleep ended, even if it began on the previous day.
        """
        endpoint = f"hrv/date/{date}/all.json"
        return cast(JSONDict, self._make_request(endpoint, user_id=user_id, debug=debug))

    @validate_date_range_params(max_days=30, resource_name="heart rate variability intraday")
    def get_hrv_intraday_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Retrieves intraday heart rate variability (HRV) data for a date range.

        This endpoint returns detailed heart rate variability measurements taken during
        sleep across multiple days, up to a maximum range of 30 days. This is useful for
        analyzing trends in recovery and stress levels over time.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-hrv-intraday-by-interval/

        Args:
            start_date: Start date in YYYY-MM-DD format or 'today'
            end_date: End date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Heart rate variability data including daily summaries and detailed measurements

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date formats are invalid
            fitbit_client.exceptions.InvalidDateRangeException: If date range is invalid or exceeds 30 days
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            The maximum date range for this endpoint is 30 days. For longer historical
            periods, you will need to make multiple requests with different date ranges.

            HRV data is collected specifically during the user's "main sleep" period
            each day. The data includes:
            - Daily summary values (dailyRmssd, deepRmssd)
            - Detailed 5-minute interval measurements throughout each sleep session

            RMSSD (Root Mean Square of Successive Differences) is measured in milliseconds,
            with higher values typically indicating better recovery and lower stress levels.

            Analyzing HRV trends over time can provide insights into:
            - Recovery status and adaptation to training
            - Stress levels and potential burnout
            - Sleep quality
            - Overall autonomic nervous system balance

            Requirements for HRV data collection:
            - Health Metrics tile enabled in the Fitbit mobile app
            - Minimum 3 hours of sleep each night
            - Sleep stages log creation (requires heart rate sensor)
            - Compatible Fitbit device

            Each day's data is associated with the date the sleep ends, even if the sleep
            session began on the previous day.
        """
        endpoint = f"hrv/date/{start_date}/{end_date}/all.json"
        return cast(JSONDict, self._make_request(endpoint, user_id=user_id, debug=debug))

    @validate_date_param(field_name="date")
    def get_spo2_intraday_by_date(
        self, date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Retrieves intraday SpO2 (blood oxygen saturation) data for a single date.

        This endpoint returns detailed SpO2 measurements taken during sleep. Blood oxygen
        saturation is an important health metric that reflects how well the body is
        supplying oxygen to the blood.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-spo2-intraday-by-date/

        Args:
            date: The date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: SpO2 data including daily summary and detailed measurements

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date format is invalid
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            SpO2 (Blood Oxygen Saturation) data is collected during the user's "main sleep"
            period (typically the longest sleep of the day). Key information:

            - SpO2 is measured as a percentage, with normal values typically ranging
              from 95-100% for healthy individuals at rest.

            - Values below 90% may indicate potential health concerns, though Fitbit
              devices are not medical devices and should not be used for diagnosis.

            - Data is calculated using a 5-minute exponentially-moving average to
              smooth out short-term fluctuations.

            - Measurements are taken approximately every 5 minutes during sleep.

            Requirements for SpO2 data collection:
            - Minimum 3 hours of quality sleep
            - Limited physical movement during sleep
            - Compatible Fitbit device with SpO2 monitoring capabilities
            - SpO2 tracking enabled in device settings

            Data processing can take up to 1 hour after device sync.
            The date represents when the sleep ended, even if it began on the previous day.
        """
        endpoint = f"spo2/date/{date}/all.json"
        return cast(JSONDict, self._make_request(endpoint, user_id=user_id, debug=debug))

    @validate_date_range_params(max_days=30, resource_name="spo2 intraday")
    def get_spo2_intraday_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-", debug: bool = False
    ) -> JSONDict:
        """Retrieves intraday SpO2 (blood oxygen saturation) data for a date range.

        This endpoint returns detailed SpO2 measurements taken during sleep across
        multiple days, up to a maximum range of 30 days. This is useful for
        analyzing trends in blood oxygen levels over time.

        API Reference: https://dev.fitbit.com/build/reference/web-api/intraday/get-spo2-intraday-by-interval/

        Args:
            start_date: Start date in YYYY-MM-DD format or 'today'
            end_date: End date in YYYY-MM-DD format or 'today'
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: SpO2 data including daily summaries and detailed measurements

        Raises:
            fitbit_client.exceptions.InvalidDateException: If date formats are invalid
            fitbit_client.exceptions.InvalidDateRangeException: If date range is invalid or exceeds 30 days
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            The maximum date range for this endpoint is 30 days. For longer historical
            periods, you will need to make multiple requests with different date ranges.

            SpO2 (Blood Oxygen Saturation) data is collected during each day's "main sleep"
            period. The data includes:
            - Daily summary values (average, minimum, maximum)
            - Detailed measurements taken approximately every 5 minutes during sleep

            SpO2 is measured as a percentage, with normal values typically ranging
            from 95-100% for healthy individuals at rest. Consistent readings below 95%
            might warrant discussion with a healthcare provider, though Fitbit devices
            are not medical devices and should not be used for diagnosis.

            Analyzing SpO2 trends over time can provide insights into:
            - Sleep quality
            - Respiratory health
            - Altitude acclimation
            - Potential sleep-related breathing disorders

            Requirements for SpO2 data collection:
            - Minimum 3 hours of quality sleep each night
            - Limited physical movement during sleep
            - Compatible Fitbit device with SpO2 monitoring capabilities
            - SpO2 tracking enabled in device settings

            Each day's data is associated with the date the sleep ends, even if the sleep
            session began on the previous day.
        """
        endpoint = f"spo2/date/{start_date}/{end_date}/all.json"
        return cast(JSONDict, self._make_request(endpoint, user_id=user_id, debug=debug))
