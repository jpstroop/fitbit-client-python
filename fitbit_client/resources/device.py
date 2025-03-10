# fitbit_client/resources/device.py

# Standard library imports
from typing import List
from typing import Optional
from typing import cast

# Local imports
from fitbit_client.resources._base import BaseResource
from fitbit_client.resources._constants import WeekDay
from fitbit_client.utils.types import JSONDict
from fitbit_client.utils.types import JSONList


class DeviceResource(BaseResource):
    """Provides access to Fitbit Device API for managing paired devices and alarms.

    This resource handles endpoints for retrieving information about devices paired to
    a user's account, as well as creating, updating, and deleting device alarms.
    The API provides device details such as battery level, version, features, sync status,
    and more.

    API Reference: https://dev.fitbit.com/build/reference/web-api/devices/

    Required Scopes: settings

    Note:
        Alarm endpoints (create, update, delete) are only supported for older Fitbit devices
        that configure alarms via the mobile application. Newer devices with on-device alarm
        applications do not support these endpoints. Currently, only the get_devices method
        is fully implemented.
    """

    def create_alarm(
        self,
        tracker_id: str,
        time: str,
        enabled: bool,
        recurring: bool,
        week_days: List[WeekDay],
        user_id: str = "-",
    ) -> JSONDict:
        """NOT IMPLEMENTED. Creates an alarm on a paired Fitbit device.

        This endpoint would allow creation of device alarms with various settings including
        time, recurrence schedule, and enabled status.

        API Reference: https://dev.fitbit.com/build/reference/web-api/devices/add-alarm/

        Args:
            tracker_id: The ID of the tracker to add the alarm to (from get_devices)
            time: Alarm time in HH:MM+XX:XX format (e.g. "07:00+00:00")
            enabled: Whether the alarm is enabled (True) or disabled (False)
            recurring: Whether the alarm repeats (True) or is a single event (False)
            week_days: List of WeekDay enum values indicating which days the alarm repeats
            user_id: Optional user ID, defaults to current user ("-")

        Returns:
            JSONDict: Details of the created alarm

        Raises:
            NotImplementedError: This method is not yet implemented

        Note:
            This endpoint only works with older Fitbit devices that configure alarms via
            the API. Newer devices with on-device alarm applications do not support this
            endpoint. This method is provided for API completeness but is not currently
            implemented in this client.
        """
        raise NotImplementedError

    def delete_alarm(self, tracker_id: str, alarm_id: str, user_id: str = "-") -> None:
        """NOT IMPLEMENTED. Deletes an alarm from a paired Fitbit device.

        This endpoint would allow deletion of existing alarms from Fitbit devices
        by specifying the tracker ID and alarm ID.

        API Reference: https://dev.fitbit.com/build/reference/web-api/devices/delete-alarm/

        Args:
            tracker_id: The ID of the tracker containing the alarm (from get_devices)
            alarm_id: The ID of the alarm to delete (from get_alarms)
            user_id: Optional user ID, defaults to current user ("-")

        Returns:
            None

        Raises:
            NotImplementedError: This method is not yet implemented

        Note:
            This endpoint only works with older Fitbit devices that configure alarms via
            the API. Newer devices with on-device alarm applications do not support this
            endpoint. This method is provided for API completeness but is not currently
            implemented in this client.
        """
        raise NotImplementedError

    def get_alarms(self, tracker_id: str, user_id: str = "-") -> JSONDict:
        """NOT IMPLEMENTED. Retrieves a list of alarms for a paired Fitbit device.

        This endpoint would return all configured alarms for a specific Fitbit device,
        including their time settings, enabled status, and recurrence patterns.

        API Reference: https://dev.fitbit.com/build/reference/web-api/devices/get-alarms/

        Args:
            tracker_id: The ID of the tracker to get alarms for (from get_devices)
            user_id: Optional user ID, defaults to current user ("-")

        Returns:
            JSONDict: Dictionary containing a list of alarms

        Raises:
            NotImplementedError: This method is not yet implemented

        Note:
            This endpoint only works with older Fitbit devices that configure alarms via
            the API. Newer devices with on-device alarm applications do not support this
            endpoint. This method is provided for API completeness but is not currently
            implemented in this client.
        """
        raise NotImplementedError

    def get_devices(self, user_id: str = "-", debug: bool = False) -> JSONList:
        """Returns a list of Fitbit devices paired to a user's account.

        This endpoint provides information about all devices connected to a user's Fitbit
        account, including trackers, watches, and scales. The data includes battery status,
        device model, features, sync status, and other device-specific information.

        API Reference: https://dev.fitbit.com/build/reference/web-api/devices/get-devices/

        Args:
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONList: List of Fitbit devices paired to the user's account with details like battery level, model, and features

        Raises:
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted

        Note:
            The exact fields returned depend on the device type. Newer devices provide
            more detailed information than older models. Some devices may return additional
            fields not listed here, such as firmware details, hardware versions, or device
            capabilities.

            The 'features' array lists device capabilities like heart rate tracking,
            GPS, SpO2 monitoring, etc. These can be used to determine what types of
            data are available for a particular device.
        """
        return cast(JSONList, self._make_request("devices.json", user_id=user_id, debug=debug))

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
        label: Optional[str] = None,
        vibe: Optional[str] = None,
        user_id: str = "-",
    ) -> JSONDict:
        """NOT IMPLEMENTED. Updates an existing alarm on a paired Fitbit device.

        This endpoint would allow modification of alarm settings including time,
        recurrence pattern, snooze settings, and labels.

        API Reference: https://dev.fitbit.com/build/reference/web-api/devices/update-alarm/

        Args:
            tracker_id: The ID of the tracker containing the alarm (from get_devices)
            alarm_id: The ID of the alarm to update (from get_alarms)
            time: Alarm time in HH:MM+XX:XX format (e.g. "07:00+00:00")
            enabled: Whether the alarm is enabled (True) or disabled (False)
            recurring: Whether the alarm repeats (True) or is a single event (False)
            week_days: List of WeekDay enum values indicating which days the alarm repeats
            snooze_length: Length of snooze in minutes
            snooze_count: Number of times the alarm can be snoozed
            label: Optional label for the alarm
            vibe: Optional vibration pattern
            user_id: Optional user ID, defaults to current user ("-")

        Returns:
            JSONDict: Details of the updated alarm

        Raises:
            NotImplementedError: This method is not yet implemented

        Note:
            This endpoint only works with older Fitbit devices that configure alarms via
            the API. Newer devices with on-device alarm applications do not support this
            endpoint. This method is provided for API completeness but is not currently
            implemented in this client.

            The available vibration patterns (vibe parameter) and supported snooze settings
            vary by device model.
        """
        raise NotImplementedError
