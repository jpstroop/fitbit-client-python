# tests/fitbit_client/resources/heartrate_timeseries/test_get_heartrate_timeseries_by_date.py

"""Tests for the get_heartrate_timeseries_by_date endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import IntradayValidationException
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import ParameterValidationException
from fitbit_client.resources._constants import Period


def test_get_heartrate_timeseries_by_date_success(
    heartrate_resource, mock_oauth_session, mock_response_factory
):
    """Test successful retrieval of heart rate data by date and period"""
    response_data = {
        "activities-heart": [
            {
                "dateTime": "2024-02-10",
                "value": {
                    "customHeartRateZones": [],
                    "heartRateZones": [
                        {
                            "name": "Out of Range",
                            "minutes": 180,
                            "caloriesOut": 500,
                            "min": 30,
                            "max": 90,
                        }
                    ],
                    "restingHeartRate": 65,
                },
            }
        ]
    }
    mock_response = mock_response_factory(200, response_data)
    mock_oauth_session.request.return_value = mock_response
    result = heartrate_resource.get_heartrate_timeseries_by_date(
        date="2024-02-10", period=Period.ONE_DAY
    )
    assert result == response_data
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/heart/date/2024-02-10/1d.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_heartrate_timeseries_by_date_today(heartrate_resource, mock_response_factory):
    """Test that 'today' is accepted as a valid date"""
    mock_response = mock_response_factory(200, {"activities-heart": []})
    heartrate_resource.oauth.request.return_value = mock_response
    result = heartrate_resource.get_heartrate_timeseries_by_date(
        date="today", period=Period.ONE_DAY
    )
    assert result == {"activities-heart": []}
    heartrate_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/heart/date/today/1d.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_heartrate_timeseries_by_date_invalid_date(heartrate_resource):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException):
        heartrate_resource.get_heartrate_timeseries_by_date(
            date="invalid-date", period=Period.ONE_DAY
        )


def test_get_heartrate_timeseries_by_date_invalid_period(heartrate_resource):
    """Test that error is raised for unsupported period"""
    with raises(IntradayValidationException) as exc_info:
        heartrate_resource.get_heartrate_timeseries_by_date(
            date="2024-02-10", period=Period.ONE_YEAR
        )
    error_msg = str(exc_info.value)
    assert "Period must be one of the supported values" in error_msg
    assert all((period in error_msg for period in ["1d", "7d", "30d", "1w", "1m"]))


def test_get_heartrate_timeseries_by_date_invalid_timezone(heartrate_resource):
    """Test that error is raised for unsupported timezone"""
    with raises(ParameterValidationException) as exc_info:
        heartrate_resource.get_heartrate_timeseries_by_date(
            date="2024-02-10", period=Period.ONE_DAY, timezone="EST"
        )
    assert str(exc_info.value) == "Only 'UTC' timezone is supported"
