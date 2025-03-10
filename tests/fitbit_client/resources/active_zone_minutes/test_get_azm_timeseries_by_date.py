# tests/fitbit_client/resources/active_zone_minutes/test_get_azm_timeseries_by_date.py

"""Tests for the get_azm_timeseries_by_date endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import IntradayValidationException
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.resources.constants import Period


def test_get_azm_timeseries_by_date_success(azm_resource, mock_response):
    """Test successful retrieval of AZM time series by date with default period"""
    mock_response.json.return_value = {
        "activities-active-zone-minutes": [
            {
                "dateTime": "2025-02-01",
                "value": {
                    "activeZoneMinutes": 102,
                    "fatBurnActiveZoneMinutes": 90,
                    "cardioActiveZoneMinutes": 8,
                    "peakActiveZoneMinutes": 4,
                },
            }
        ]
    }
    azm_resource.oauth.request.return_value = mock_response
    result = azm_resource.get_azm_timeseries_by_date(date="2025-02-01")
    assert result == mock_response.json.return_value
    azm_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/2025-02-01/1d.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_azm_timeseries_by_date_explicit_period(azm_resource, mock_response):
    """Test successful retrieval of AZM time series by date with explicit ONE_DAY period"""
    mock_response.json.return_value = {"activities-active-zone-minutes": []}
    azm_resource.oauth.request.return_value = mock_response
    result = azm_resource.get_azm_timeseries_by_date(date="2025-02-01", period=Period.ONE_DAY)
    assert result == mock_response.json.return_value
    azm_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/2025-02-01/1d.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_azm_timeseries_by_date_with_user_id(azm_resource, mock_response):
    """Test getting AZM time series for a specific user"""
    mock_response.json.return_value = {"activities-active-zone-minutes": []}
    azm_resource.oauth.request.return_value = mock_response
    result = azm_resource.get_azm_timeseries_by_date(date="2025-02-01", user_id="123ABC")
    assert result == mock_response.json.return_value
    azm_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/123ABC/activities/active-zone-minutes/date/2025-02-01/1d.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_azm_timeseries_by_date_invalid_period(azm_resource):
    """Test that using any period other than ONE_DAY raises IntradayValidationException"""
    invalid_periods = [
        Period.SEVEN_DAYS,
        Period.THIRTY_DAYS,
        Period.ONE_WEEK,
        Period.ONE_MONTH,
        Period.THREE_MONTHS,
        Period.SIX_MONTHS,
        Period.ONE_YEAR,
        Period.MAX,
    ]
    for period in invalid_periods:
        with raises(IntradayValidationException) as exc_info:
            azm_resource.get_azm_timeseries_by_date(date="2025-02-01", period=period)
        assert "Only 1d period is supported for AZM time series" in str(exc_info.value)
        assert exc_info.value.field_name == "period"
        assert exc_info.value.allowed_values == ["1d"]
        assert exc_info.value.resource_name == "active zone minutes"


def test_get_azm_timeseries_by_date_invalid_date(azm_resource):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException) as exc_info:
        azm_resource.get_azm_timeseries_by_date(date="invalid-date")
    assert "invalid-date" in str(exc_info.value)
    assert exc_info.value.field_name == "date"
