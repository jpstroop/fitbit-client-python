# tests/resources/activity/test_create_activity_log.py

"""Tests for the create_activity_log endpoint."""

# Standard library imports
from unittest.mock import Mock

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


# Success cases - Activity ID path
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


def test_create_activity_log_with_distance_and_unit(activity_resource):
    """Test creating activity log with distance and distance unit"""
    activity_resource._make_request = Mock()
    activity_resource.create_activity_log(
        activity_id=123,
        start_time="12:00",
        duration_millis=3600000,
        date="2023-01-01",
        distance=5.0,
        distance_unit="km",
    )
    expected_params = {
        "activityId": 123,
        "startTime": "12:00",
        "durationMillis": 3600000,
        "date": "2023-01-01",
        "distance": 5.0,
        "distanceUnit": "km",
    }
    activity_resource._make_request.assert_called_once_with(
        "activities.json", params=expected_params, user_id="-", http_method="POST", debug=False
    )


# Success cases - Custom activity path
def test_create_activity_log_with_custom_activity(activity_resource):
    """Test creating activity log with custom activity name and manual calories"""
    activity_resource._make_request = Mock()
    activity_resource.create_activity_log(
        activity_name="Custom Yoga",
        manual_calories=250,
        start_time="12:00",
        duration_millis=3600000,
        date="2023-01-01",
    )
    expected_params = {
        "activityName": "Custom Yoga",
        "manualCalories": 250,
        "startTime": "12:00",
        "durationMillis": 3600000,
        "date": "2023-01-01",
    }
    activity_resource._make_request.assert_called_once_with(
        "activities.json", params=expected_params, user_id="-", http_method="POST", debug=False
    )


# Error cases
def test_create_activity_log_invalid_date(activity_resource):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException) as exc_info:
        activity_resource.create_activity_log(
            activity_id=123, start_time="12:00", duration_millis=3600000, date="invalid-date"
        )
    assert "invalid-date" in str(exc_info.value)
    assert exc_info.value.field_name == "date"


def test_create_activity_log_missing_required_params(activity_resource):
    """Test that missing required parameters raises ValueError"""
    with raises(ValueError) as exc_info:
        activity_resource.create_activity_log(
            start_time="12:00", duration_millis=3600000, date="2023-01-01"
        )

    assert "Must provide either activity_id or (activity_name and manual_calories)" in str(
        exc_info.value
    )


def test_create_activity_log_partial_custom_params(activity_resource):
    """Test that providing only activity_name without manual_calories raises ValueError"""
    with raises(ValueError) as exc_info:
        activity_resource.create_activity_log(
            activity_name="Custom Yoga",
            start_time="12:00",
            duration_millis=3600000,
            date="2023-01-01",
        )

    assert "Must provide either activity_id or (activity_name and manual_calories)" in str(
        exc_info.value
    )
