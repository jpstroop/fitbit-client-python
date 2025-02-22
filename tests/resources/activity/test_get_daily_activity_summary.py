# tests/resources/activity/test_get_daily_activity_summary.py

"""Tests for the get_daily_activity_summary endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_get_daily_activity_summary_success(activity_resource):
    """Test getting daily activity summary"""
    activity_resource._make_request = Mock()
    activity_resource.get_daily_activity_summary("2023-01-01")
    activity_resource._make_request.assert_called_once_with(
        "activities/date/2023-01-01.json", user_id="-", debug=False
    )


def test_get_daily_activity_summary_invalid_date(activity_resource):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException) as exc_info:
        activity_resource.get_daily_activity_summary("invalid-date")
    assert "invalid-date" in str(exc_info.value)
    assert exc_info.value.field_name == "date"
