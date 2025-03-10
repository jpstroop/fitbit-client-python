# tests/fitbit_client/resources/heartrate_variability/test_get_hrv_summary_by_date.py

"""Tests for the get_hrv_summary_by_date endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_get_hrv_summary_by_date_success(hrv_resource, mock_oauth_session, mock_response_factory):
    """Test successful retrieval of HRV data for a single date"""
    expected_response = {
        "hrv": [{"dateTime": "2024-02-13", "value": {"dailyRmssd": 34.938, "deepRmssd": 31.567}}]
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response
    result = hrv_resource.get_hrv_summary_by_date("2024-02-13")
    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/hrv/date/2024-02-13.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_hrv_summary_by_date_today(hrv_resource, mock_oauth_session, mock_response_factory):
    """Test HRV data retrieval using 'today' as date parameter"""
    mock_response = mock_response_factory(200, {"hrv": []})
    mock_oauth_session.request.return_value = mock_response
    hrv_resource.get_hrv_summary_by_date("today")


def test_get_hrv_summary_by_date_invalid_date(hrv_resource):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException):
        hrv_resource.get_hrv_summary_by_date("invalid-date")
