# tests/resources/breathing_rate/test_get_breathingrate_summary_by_interval.py

"""Tests for the get_breathing_rate_summary_by_interval endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateRangeException


def test_get_by_interval_validates_date_range(breathing_rate_resource):
    """Test that exceeding 30-day range limit raises InvalidDateRangeException"""
    start_date = "2023-01-01"
    end_date = "2023-02-01"
    with raises(InvalidDateRangeException) as exc_info:
        breathing_rate_resource.get_breathing_rate_summary_by_interval(start_date, end_date)
    assert f"Date range {start_date} to {end_date} exceeds maximum allowed 30 days" in str(
        exc_info.value
    )


def test_get_by_interval_validates_date_order(breathing_rate_resource):
    """Test that start date must be before or equal to end date"""
    start_date = "2023-01-15"
    end_date = "2023-01-01"
    with raises(InvalidDateRangeException) as exc_info:
        breathing_rate_resource.get_breathing_rate_summary_by_interval(start_date, end_date)
    assert f"Start date {start_date} is after end date {end_date}" in str(exc_info.value)


def test_get_by_interval_allows_same_date(breathing_rate_resource):
    """Test that same start and end date is allowed"""
    breathing_rate_resource._make_request = Mock()
    breathing_rate_resource.get_breathing_rate_summary_by_interval("2023-01-01", "2023-01-01")
    breathing_rate_resource._make_request.assert_called_once()
