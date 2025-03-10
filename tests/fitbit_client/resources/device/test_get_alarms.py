# tests/fitbit_client/resources/device/test_get_alarms.py

"""Tests for the get_alarms endpoint."""

# Third party imports

# Third party imports
from pytest import raises


def test_get_alarms_not_implemented(device_resource):
    """Test get_alarms raises NotImplementedError."""
    with raises(NotImplementedError):
        device_resource.get_alarms(tracker_id="123")
