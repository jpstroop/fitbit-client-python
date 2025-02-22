# tests/resources/activity/test_create_activity_log.py

"""Tests for the create_activity_log endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_create_activity_log_with_activity_id_only(activity_resource):
    """Test creating activity log with just an activity ID"""
    activity_resource._make_request = Mock()
    activity_resource.create_activity_log(
        activity_id=123, start_time="12:00", duration_millis=3600000, date="2023-01-01"
    )
    expected_params = {
        "activityId": 123,
        "startTime": "12:00",
        "durationMillis": 3600000,
        "date": "2023-01-01",
    }
    activity_resource._make_request.assert_called_once_with(
        "activities.json", params=expected_params, user_id="-", http_method="POST", debug=False
    )


def test_create_activity_log_with_distance_no_unit(activity_resource):
    """Test creating activity log with distance but no distance unit"""
    activity_resource._make_request = Mock()
    activity_resource.create_activity_log(
        activity_id=123,
        start_time="12:00",
        duration_millis=3600000,
        date="2023-01-01",
        distance=5.0,
    )
    expected_params = {
        "activityId": 123,
        "startTime": "12:00",
        "durationMillis": 3600000,
        "date": "2023-01-01",
        "distance": 5.0,
    }
    activity_resource._make_request.assert_called_once_with(
        "activities.json", params=expected_params, user_id="-", http_method="POST", debug=False
    )


def test_create_activity_log_invalid_date(activity_resource):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException) as exc_info:
        activity_resource.create_activity_log(
            activity_id=123, start_time="12:00", duration_millis=3600000, date="invalid-date"
        )
    assert "invalid-date" in str(exc_info.value)
    assert exc_info.value.field_name == "date"
