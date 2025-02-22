# tests/resources/body_timeseries/test_get_weight_timeseries_by_date.py

"""Tests for the get_weight_timeseries_by_date endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.resources.constants import BodyTimePeriod


def test_get_weight_timeseries_by_date_validates_date(body_timeseries):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException) as exc_info:
        body_timeseries.get_weight_timeseries_by_date(
            date="invalid-date", period=BodyTimePeriod.ONE_MONTH
        )
    assert exc_info.value.field_name == "date"
    assert "Invalid date format" in str(exc_info.value)
