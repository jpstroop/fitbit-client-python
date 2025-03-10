# tests/fitbit_client/resources/active_zone_minutes/test_get_azm_timeseries_by_interval.py

"""Tests for the get_azm_timeseries_by_interval endpoint."""

# Third party imports

# Standard library imports
from datetime import datetime
from datetime import timedelta

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException


def test_get_azm_timeseries_by_interval_success(azm_resource, mock_response_factory):
    """Test successful retrieval of AZM time series by date range"""
    expected_data = {
        "activities-active-zone-minutes": [
            {
                "dateTime": "2025-02-01",
                "value": {
                    "activeZoneMinutes": 102,
                    "fatBurnActiveZoneMinutes": 90,
                    "cardioActiveZoneMinutes": 8,
                    "peakActiveZoneMinutes": 4,
                },
            },
            {
                "dateTime": "2025-02-02",
                "value": {
                    "activeZoneMinutes": 47,
                    "fatBurnActiveZoneMinutes": 43,
                    "cardioActiveZoneMinutes": 4,
                },
            },
        ]
    }
    mock_response = mock_response_factory(200, expected_data)
    azm_resource.oauth.request.return_value = mock_response
    result = azm_resource.get_azm_timeseries_by_interval(
        start_date="2025-02-01", end_date="2025-02-02"
    )
    assert result == expected_data
    azm_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/2025-02-01/2025-02-02.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_azm_timeseries_by_interval_with_user_id(azm_resource, mock_response_factory):
    """Test getting AZM time series by date range for a specific user"""
    expected_data = {"activities-active-zone-minutes": []}
    mock_response = mock_response_factory(200, expected_data)
    azm_resource.oauth.request.return_value = mock_response
    result = azm_resource.get_azm_timeseries_by_interval(
        start_date="2025-02-01", end_date="2025-02-02", user_id="123ABC"
    )
    assert result == expected_data
    azm_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/123ABC/activities/active-zone-minutes/date/2025-02-01/2025-02-02.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_azm_timeseries_by_interval_invalid_dates(azm_resource):
    """Test that invalid date formats raise InvalidDateException"""
    with raises(InvalidDateException) as exc_info:
        azm_resource.get_azm_timeseries_by_interval(start_date="invalid", end_date="2024-02-01")
    assert "invalid" in str(exc_info.value)
    assert exc_info.value.field_name == "start_date"
    with raises(InvalidDateException) as exc_info:
        azm_resource.get_azm_timeseries_by_interval(start_date="2024-02-01", end_date="invalid")
    assert "invalid" in str(exc_info.value)
    assert exc_info.value.field_name == "end_date"


def test_get_azm_timeseries_by_interval_invalid_date_order(azm_resource):
    """Test that start_date after end_date raises InvalidDateRangeException"""
    with raises(InvalidDateRangeException) as exc_info:
        azm_resource.get_azm_timeseries_by_interval(start_date="2025-02-02", end_date="2025-02-01")
    assert "Start date 2025-02-02 is after end date 2025-02-01" in str(exc_info.value)


def test_get_azm_timeseries_by_interval_exceeds_max_range(azm_resource):
    """Test that exceeding the 1095 day range limit raises InvalidDateRangeException"""
    start_date = (datetime.now() - timedelta(days=1096)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    with raises(InvalidDateRangeException) as exc_info:
        azm_resource.get_azm_timeseries_by_interval(start_date=start_date, end_date=end_date)
    assert "1095 days" in str(exc_info.value)
    assert "AZM time series" in str(exc_info.value)
