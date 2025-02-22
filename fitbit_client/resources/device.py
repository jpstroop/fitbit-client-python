# fitbit_client/resources/device.py

# Standard library imports
from typing import Any
from typing import Dict
from typing import List

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import WeekDay


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
        NOT IMPLEMENTED. Create an alarm for a device.
        """
        raise NotImplementedError

    def delete_alarm(self, tracker_id: str, alarm_id: str, user_id: str = "-") -> Dict[str, Any]:
        """
        NOT IMPLEMENTED. Delete an alarm from a device.
        """
        raise NotImplementedError

    def get_alarms(self, tracker_id: str, user_id: str = "-") -> Dict[str, Any]:
        """
        NOT IMPLEMENTED. Get list of alarms for a device.
        """
        raise NotImplementedError

    def get_devices(self, user_id: str = "-", debug: bool = False) -> Dict[str, Any]:
        """
        Get list of Fitbit devices paired to a user's account.

        API Reference: https://dev.fitbit.com/build/reference/web-api/devices/get-devices/

        Args:
            user_id: Optional user ID, defaults to current user
            debug: If True, a prints a curl command to stdout to help with debugging (default: False)

        Returns:
            Response contains list of paired devices with their details including:
            battery level, device version, features, last sync time, etc.
        """
        return self._make_request("devices.json", user_id=user_id, debug=debug)

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
        NOT IMPLEMENTED. Update an existing alarm on a device.
        """
        raise NotImplementedError
