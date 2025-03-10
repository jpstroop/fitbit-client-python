# tests/fitbit_client/resources/heartrate_timeseries/test_get_heartrate_timeseries_by_date_range.py

"""Tests for the get_heartrate_timeseries_by_date_range endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException
from fitbit_client.exceptions import ParameterValidationException


def test_get_heartrate_timeseries_by_date_range_success(heartrate_resource, mock_response_factory):
    """Test successful retrieval of heart rate data by date range"""
    response_data = {
        "activities-heart": [
            {"dateTime": "2024-02-10", "value": {"restingHeartRate": 65, "heartRateZones": []}},
            {"dateTime": "2024-02-11", "value": {"restingHeartRate": 68, "heartRateZones": []}},
        ]
    }
    mock_response = mock_response_factory(200, response_data)
    heartrate_resource.oauth.request.return_value = mock_response
    result = heartrate_resource.get_heartrate_timeseries_by_date_range(
        start_date="2024-02-10", end_date="2024-02-11"
    )
    assert result == response_data
    heartrate_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/heart/date/2024-02-10/2024-02-11.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_heartrate_timeseries_by_date_range_today(heartrate_resource, mock_response_factory):
    """Test that 'today' is accepted in date range"""
    mock_response = mock_response_factory(200, {"activities-heart": []})
    heartrate_resource.oauth.request.return_value = mock_response
    result = heartrate_resource.get_heartrate_timeseries_by_date_range(
        start_date="today", end_date="today"
    )
    assert result == {"activities-heart": []}
    heartrate_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/heart/date/today/today.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_heartrate_timeseries_by_date_range_invalid_dates(heartrate_resource):
    """Test that invalid date formats raise InvalidDateException"""
    with raises(InvalidDateException):
        heartrate_resource.get_heartrate_timeseries_by_date_range(
            start_date="invalid", end_date="2024-02-11"
        )
    with raises(InvalidDateException):
        heartrate_resource.get_heartrate_timeseries_by_date_range(
            start_date="2024-02-10", end_date="invalid"
        )


def test_get_heartrate_timeseries_by_date_range_invalid_range(heartrate_resource):
    """Test that end date before start date raises InvalidDateRangeException"""
    with raises(InvalidDateRangeException):
        heartrate_resource.get_heartrate_timeseries_by_date_range(
            start_date="2024-02-11", end_date="2024-02-10"
        )


def test_get_heartrate_timeseries_by_date_range_invalid_timezone(heartrate_resource):
    """Test that invalid timezone raises ParameterValidationException"""
    with raises(ParameterValidationException) as exc_info:
        heartrate_resource.get_heartrate_timeseries_by_date_range(
            start_date="2024-02-10", end_date="2024-02-11", timezone="EST"
        )
    assert str(exc_info.value) == "Only 'UTC' timezone is supported"
    assert exc_info.value.field_name == "timezone"
