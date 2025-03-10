# tests/fitbit_client/resources/cardio_fitness_score/test_get_vo2_max_summary_by_date.py

"""Tests for the get_vo2_max_summary_by_date endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_get_by_date_validates_date_format(cardio_fitness_score_resource):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException) as exc_info:
        cardio_fitness_score_resource.get_vo2_max_summary_by_date("invalid-date")
    assert exc_info.value.field_name == "date"
    assert "Invalid date format" in str(exc_info.value)


def test_get_by_date_allows_today(cardio_fitness_score_resource):
    """Test that 'today' is accepted as a valid date"""
    cardio_fitness_score_resource._make_request = Mock()
    cardio_fitness_score_resource.get_vo2_max_summary_by_date("today")
    cardio_fitness_score_resource._make_request.assert_called_once()


def test_get_by_date_allows_valid_date(cardio_fitness_score_resource):
    """Test that valid date format is accepted"""
    cardio_fitness_score_resource._make_request = Mock()
    cardio_fitness_score_resource.get_vo2_max_summary_by_date("2023-01-01")
    cardio_fitness_score_resource._make_request.assert_called_once()
