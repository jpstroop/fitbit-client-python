# tests/resources/body_timeseries/test_get_bodyfat_timeseries_by_date_range.py

"""Tests for the get_bodyfat_timeseries_by_date_range endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_get_bodyfat_timeseries_by_date_range_validates_dates(body_timeseries):
    """Test that invalid dates raise InvalidDateException"""
    with raises(InvalidDateException):
        body_timeseries.get_bodyfat_timeseries_by_date_range(
            start_date="invalid-date", end_date="2023-01-01"
        )
    with raises(InvalidDateException):
        body_timeseries.get_bodyfat_timeseries_by_date_range(
            start_date="2023-01-01", end_date="invalid-date"
        )
