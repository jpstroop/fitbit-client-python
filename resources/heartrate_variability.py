# resources/heartrate_variability.py
from typing import Any
from typing import Dict

from resources.base import BaseResource


class HeartRateVariabilityResource(BaseResource):
    """
    Handles Fitbit Heart Rate Variability (HRV) API endpoints for retrieving daily and interval HRV data.

    API Reference: https://dev.fitbit.com/build/reference/web-api/heartrate-variability/

    Note:
        This resource requires the 'heartrate' scope.
        HRV data is collected only during the user's "main sleep" (longest sleep period) and requires:
        - Enabled Health Metrics tile in mobile app dashboard
        - Minimum 3 hours of sleep
        - Creation of sleep stages log during main sleep period
        - Device compatibility (check Fitbit Product page for supported devices)

        Data processing occurs after device sync and takes ~15 minutes to become available.
        HRV measurements span sleep periods that may begin on the previous day.
        Premium subscription is not required for HRV data collection.
    """

    def get_hrv_summary_by_date(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Retrieves HRV summary data for a single date.

        Args:
            date: Date in yyyy-MM-dd format or 'today'
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.

        Returns:
            HRV data including:
            - dateTime: Sleep log date
            - value:
                - dailyRmssd: Daily heart rate variability (RMSSD) in milliseconds
                - deepRmssd: Deep sleep heart rate variability (RMSSD) in milliseconds

        Note:
            Data reflects the main sleep period, which may have started the previous day.
            A 200 status code indicates successful execution, even if no data exists.
            For reliable data collection, users should remain still during sleep measurement.
        """
        return self._get(f"hrv/date/{date}.json", user_id=user_id)

    def get_hrv_summary_by_interval(self, start_date: str, end_date: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Retrieves HRV summary data for a date range.

        Args:
            start_date: Start date in yyyy-MM-dd format or 'today'
            end_date: End date in yyyy-MM-dd format or 'today'
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.

        Returns:
            HRV data for each date including:
            - dateTime: Sleep log date
            - value:
                - dailyRmssd: Daily heart rate variability (RMSSD) in milliseconds
                - deepRmssd: Deep sleep heart rate variability (RMSSD) in milliseconds

        Note:
            Maximum date range is 30 days.
            Data reflects main sleep periods, which may have started the day before each date.
            A 200 status code indicates successful execution, even if no data exists.
            Since HRV data requires sleep, consider querying once or twice daily (e.g., noon and midnight).
        """
        return self._get(f"hrv/date/{start_date}/{end_date}.json", user_id=user_id)
