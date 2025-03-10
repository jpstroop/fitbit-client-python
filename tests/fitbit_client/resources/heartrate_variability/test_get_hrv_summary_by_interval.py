# tests/fitbit_client/resources/heartrate_variability/test_get_hrv_summary_by_interval.py

"""Tests for the get_hrv_summary_by_interval endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException


def test_get_hrv_summary_by_interval_success(
    hrv_resource, mock_oauth_session, mock_response_factory
):
    """Test successful retrieval of HRV data for a date range"""
    expected_response = {
        "hrv": [
            {"dateTime": "2024-02-13", "value": {"dailyRmssd": 62.887, "deepRmssd": 64.887}},
            {"dateTime": "2024-02-14", "value": {"dailyRmssd": 61.887, "deepRmssd": 64.887}},
        ]
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response
    result = hrv_resource.get_hrv_summary_by_interval("2024-02-13", "2024-02-14")
    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/hrv/date/2024-02-13/2024-02-14.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_hrv_summary_by_interval_today(hrv_resource, mock_oauth_session, mock_response_factory):
    """Test that 'today' is accepted in date range"""
    mock_response = mock_response_factory(200, {"hrv": []})
    mock_oauth_session.request.return_value = mock_response
    hrv_resource.get_hrv_summary_by_interval("today", "today")


def test_get_hrv_summary_by_interval_invalid_dates(hrv_resource):
    """Test that invalid date formats raise InvalidDateException"""
    with raises(InvalidDateException):
        hrv_resource.get_hrv_summary_by_interval("invalid", "2024-02-14")
    with raises(InvalidDateException):
        hrv_resource.get_hrv_summary_by_interval("2024-02-13", "invalid")


def test_get_hrv_summary_by_interval_invalid_range(hrv_resource):
    """Test that end date before start date raises InvalidDateRangeException"""
    with raises(InvalidDateRangeException):
        hrv_resource.get_hrv_summary_by_interval("2024-02-14", "2024-02-13")
