# Standard library imports
from typing import Any
from typing import Dict
from typing import List

# Third party imports
from resources.base import BaseResource
from resources.constants import WeekDay


class DeviceResource(BaseResource):
    """
    Handles Fitbit Device API endpoints for managing devices and their alarms.

    Note:
        Alarm endpoints are only supported for older devices that configure alarms via
        the mobile application. Newer devices with on-device alarm applications do not
        support these endpoints.

    API Reference: https://dev.fitbit.com/build/reference/web-api/devices/
    """

    def create_alarm(
        self,
        tracker_id: str,
        time: str,
        enabled: bool,
        recurring: bool,
        week_days: List[WeekDay],
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Create an alarm for a device.

        Args:
            tracker_id: ID of the tracker to create the alarm for
            time: Time in HH:mm-offset format (e.g. "07:00-08:00")
            enabled: Whether the alarm is enabled
            recurring: Whether the alarm is recurring
            week_days: List of days when the alarm should trigger
            user_id: Optional user ID, defaults to current user

        Returns:
            Response contains the created alarm settings
        """
        params = {
            "time": time,
            "enabled": str(enabled).lower(),
            "recurring": str(recurring).lower(),
            "weekDays": ",".join(day.value for day in week_days),
        }
        return self._make_request(
            f"devices/tracker/{tracker_id}/alarms.json",
            params=params,
            user_id=user_id,
            http_method="POST",
        )

    def delete_alarm(self, tracker_id: str, alarm_id: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Delete an alarm from a device.

        Args:
            tracker_id: ID of the tracker that has the alarm
            alarm_id: ID of the alarm to delete
            user_id: Optional user ID, defaults to current user
        """
        return self._make_request(
            f"devices/tracker/{tracker_id}/alarms/{alarm_id}.json",
            user_id=user_id,
            http_method="DELETE",
        )

    def get_alarms(self, tracker_id: str, user_id: str = "-") -> Dict[str, Any]:
        """
        Get list of alarms for a device.

        Args:
            tracker_id: ID of the tracker to get alarms for
            user_id: Optional user ID, defaults to current user

        Returns:
            Response contains list of alarms configured for the device
        """
        return self._make_request(f"devices/tracker/{tracker_id}/alarms.json", user_id=user_id)

    def get_devices(self, user_id: str = "-") -> Dict[str, Any]:
        """
        Get list of Fitbit devices paired to a user's account.

        Args:
            user_id: Optional user ID, defaults to current user

        Returns:
            Response contains list of paired devices with their details including:
            battery level, device version, features, last sync time, etc.
        """
        return self._make_request("devices.json", user_id=user_id)

    def update_alarm(
        self,
        tracker_id: str,
        alarm_id: str,
        time: str,
        enabled: bool,
        recurring: bool,
        week_days: List[WeekDay],
        snooze_length: int,
        snooze_count: int,
        label: str = None,
        vibe: str = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Update an existing alarm on a device.

        Args:
            tracker_id: ID of the tracker with the alarm
            alarm_id: ID of the alarm to update
            time: Time in HH:mm-offset format (e.g. "07:00-08:00")
            enabled: Whether the alarm is enabled
            recurring: Whether the alarm is recurring
            week_days: List of days when the alarm should trigger
            snooze_length: Minutes between snoozes
            snooze_count: Maximum number of snoozes
            label: Optional label for the alarm
            vibe: Optional vibration pattern (only "DEFAULT" supported)
            user_id: Optional user ID, defaults to current user

        Returns:
            Response contains the updated alarm settings
        """
        params = {
            "time": time,
            "enabled": str(enabled).lower(),
            "recurring": str(recurring).lower(),
            "weekDays": ",".join(day.value for day in week_days),
            "snoozeLength": snooze_length,
            "snoozeCount": snooze_count,
        }
        if label:
            params["label"] = label
        if vibe:
            params["vibe"] = vibe

        return self._make_request(
            f"devices/tracker/{tracker_id}/alarms/{alarm_id}.json",
            params=params,
            user_id=user_id,
            http_method="POST",
        )
