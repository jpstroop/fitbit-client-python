# tests/fitbit_client/resources/device/test_delete_alarm.py

"""Tests for the delete_alarm endpoint."""

# Third party imports

# Third party imports
from pytest import raises


def test_delete_alarm_not_implemented(device_resource):
    """Test delete_alarm raises NotImplementedError."""
    with raises(NotImplementedError):
        device_resource.delete_alarm(tracker_id="123", alarm_id="456")
