# tests/fitbit_client/resources/device/test_update_alarm.py

"""Tests for the update_alarm endpoint."""

# Third party imports

# Third party imports
from pytest import raises


def test_update_alarm_not_implemented(device_resource):
    """Test update_alarm raises NotImplementedError."""
    with raises(NotImplementedError):
        device_resource.update_alarm(
            tracker_id="123",
            alarm_id="456",
            time="07:00-08:00",
            enabled=True,
            recurring=True,
            week_days=["MONDAY"],
            snooze_length=5,
            snooze_count=3,
        )
