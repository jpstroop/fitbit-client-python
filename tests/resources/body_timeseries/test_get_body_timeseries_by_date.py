# tests/resources/body_timeseries/test_get_body_timeseries_by_date.py

"""Tests for the get_body_timeseries_by_date endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.constants import BodyResourceType
from fitbit_client.resources.constants import BodyTimePeriod


def test_get_body_timeseries_by_date_validates_date_format(body_timeseries):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException) as exc_info:
        body_timeseries.get_body_timeseries_by_date(
            resource_type=BodyResourceType.BMI, date="invalid-date", period=BodyTimePeriod.ONE_MONTH
        )
    assert exc_info.value.field_name == "date"
    assert "Invalid date format" in str(exc_info.value)


def test_get_body_timeseries_by_date_period_validation(body_timeseries):
    """Test period validation for fat/weight resources"""
    invalid_periods = [
        BodyTimePeriod.THREE_MONTHS,
        BodyTimePeriod.SIX_MONTHS,
        BodyTimePeriod.ONE_YEAR,
        BodyTimePeriod.MAX,
    ]
    for resource_type in (BodyResourceType.FAT, BodyResourceType.WEIGHT):
        for period in invalid_periods:
            with raises(ValidationException) as exc_info:
                body_timeseries.get_body_timeseries_by_date(
                    resource_type=resource_type, date="2023-01-01", period=period
                )
            assert exc_info.value.field_name == "period"
            assert f"Period {period.value} not supported for {resource_type.value}" in str(
                exc_info.value
            )


def test_get_body_timeseries_by_date_allows_today(body_timeseries):
    """Test that 'today' is accepted as valid date"""
    body_timeseries._make_request = Mock()
    body_timeseries.get_body_timeseries_by_date(
        resource_type=BodyResourceType.BMI, date="today", period=BodyTimePeriod.ONE_MONTH
    )
    body_timeseries._make_request.assert_called_once()
