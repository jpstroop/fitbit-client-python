# tests/resources/sleep/test_get_sleep_log_by_date.py

"""Tests for the get_sleep_log_by_date endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_get_sleep_log_by_date_success(sleep_resource, mock_oauth_session, mock_response_factory):
    """Test successful retrieval of sleep log by date"""
    expected_response = {
        "sleep": [{"dateOfSleep": "2024-02-13", "duration": 28800000, "efficiency": 90}]
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response
    result = sleep_resource.get_sleep_log_by_date("2024-02-13")
    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1.2/user/-/sleep/date/2024-02-13.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_sleep_log_by_date_invalid_date(sleep_resource):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException):
        sleep_resource.get_sleep_log_by_date("invalid-date")


def test_get_sleep_log_by_date_allows_today(
    sleep_resource, mock_oauth_session, mock_response_factory
):
    """Test that 'today' is accepted as a valid date"""
    mock_response = mock_response_factory(200, {"sleep": []})
    mock_oauth_session.request.return_value = mock_response
    sleep_resource.get_sleep_log_by_date("today")
