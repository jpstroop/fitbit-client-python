# tests/fitbit_client/resources/device/test_create_alarm.py

"""Tests for the create_alarm endpoint."""

# Third party imports

# Third party imports
from pytest import raises


def test_create_alarm_not_implemented(device_resource):
    """Test create_alarm raises NotImplementedError."""
    with raises(NotImplementedError):
        device_resource.create_alarm(
            tracker_id="123", time="07:00-08:00", enabled=True, recurring=True, week_days=["MONDAY"]
        )
