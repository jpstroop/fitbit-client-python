# tests/resources/cardio_fitness_score/test_get_vo2_max_summary_by_interval.py

"""Tests for the get_vo2_max_summary_by_interval endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException


def test_get_by_interval_validates_date_format(cardio_fitness_score_resource):
    """Test that invalid date format in interval raises InvalidDateException"""
    with raises(InvalidDateException) as exc_info:
        cardio_fitness_score_resource.get_vo2_max_summary_by_interval("2023-01-01", "invalid-date")
    assert exc_info.value.field_name == "end_date"
    assert "Invalid date format" in str(exc_info.value)
    with raises(InvalidDateException) as exc_info:
        cardio_fitness_score_resource.get_vo2_max_summary_by_interval("invalid-date", "2023-01-01")
    assert exc_info.value.field_name == "start_date"
    assert "Invalid date format" in str(exc_info.value)


def test_get_by_interval_validates_range_limit(cardio_fitness_score_resource):
    """Test that exceeding 30-day range limit raises InvalidDateRangeException"""
    start_date = "2023-01-01"
    end_date = "2023-02-01"
    with raises(InvalidDateRangeException) as exc_info:
        cardio_fitness_score_resource.get_vo2_max_summary_by_interval(start_date, end_date)
    assert f"Date range {start_date} to {end_date} exceeds maximum allowed 30 days" in str(
        exc_info.value
    )


def test_get_by_interval_validates_date_order(cardio_fitness_score_resource):
    """Test that start date must be before or equal to end date"""
    start_date = "2023-01-15"
    end_date = "2023-01-01"
    with raises(InvalidDateRangeException) as exc_info:
        cardio_fitness_score_resource.get_vo2_max_summary_by_interval(start_date, end_date)
    assert f"Start date {start_date} is after end date {end_date}" in str(exc_info.value)


def test_get_by_interval_allows_valid_range(cardio_fitness_score_resource):
    """Test that valid date range is accepted"""
    cardio_fitness_score_resource._make_request = Mock()
    cardio_fitness_score_resource.get_vo2_max_summary_by_interval("2023-01-01", "2023-01-15")
    cardio_fitness_score_resource._make_request.assert_called_once()


def test_get_by_interval_allows_today(cardio_fitness_score_resource):
    """Test that 'today' is accepted in interval endpoints"""
    cardio_fitness_score_resource._make_request = Mock()
    cardio_fitness_score_resource.get_vo2_max_summary_by_interval("today", "today")
    cardio_fitness_score_resource._make_request.assert_called_once()


def test_get_by_interval_allows_same_date(cardio_fitness_score_resource):
    """Test that same start and end date is allowed"""
    cardio_fitness_score_resource._make_request = Mock()
    cardio_fitness_score_resource.get_vo2_max_summary_by_interval("2023-01-01", "2023-01-01")
    cardio_fitness_score_resource._make_request.assert_called_once()
