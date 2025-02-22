# tests/resources/breathing_rate/test_get_breathingrate_summary_by_date.py

"""Tests for the get_breathing_rate_summary_by_date endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_get_by_date_validates_date_format(breathing_rate_resource):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException) as exc_info:
        breathing_rate_resource.get_breathing_rate_summary_by_date("invalid-date")
    assert exc_info.value.field_name == "date"
    assert "Invalid date format" in str(exc_info.value)


def test_get_by_date_allows_today(breathing_rate_resource):
    """Test that 'today' is accepted as a valid date"""
    breathing_rate_resource._make_request = Mock()
    breathing_rate_resource.get_breathing_rate_summary_by_date("today")
    breathing_rate_resource._make_request.assert_called_once()
