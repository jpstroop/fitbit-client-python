# tests/fitbit_client/resources/sleep/test_get_sleep_log_by_date_range.py

"""Tests for the get_sleep_log_by_date_range endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException


def test_get_sleep_log_by_date_range_success(
    sleep_resource, mock_oauth_session, mock_response_factory
):
    """Test successful retrieval of sleep log by date range"""
    expected_response = {
        "sleep": [
            {"dateOfSleep": "2024-02-13", "duration": 28800000},
            {"dateOfSleep": "2024-02-14", "duration": 27000000},
        ]
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response
    result = sleep_resource.get_sleep_log_by_date_range("2024-02-13", "2024-02-14")
    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1.2/user/-/sleep/date/2024-02-13/2024-02-14.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_sleep_log_by_date_range_exceeds_max_days(sleep_resource):
    """Test that exceeding 100 days raises InvalidDateRangeException"""
    with raises(InvalidDateRangeException) as exc_info:
        sleep_resource.get_sleep_log_by_date_range("2024-02-13", "2024-05-24")
    assert "Date range 2024-02-13 to 2024-05-24 exceeds maximum allowed 100 days" in str(
        exc_info.value
    )


def test_get_sleep_log_by_date_range_invalid_dates(sleep_resource):
    """Test that invalid date formats raise InvalidDateException"""
    with raises(InvalidDateException):
        sleep_resource.get_sleep_log_by_date_range("invalid", "2024-02-14")
    with raises(InvalidDateException):
        sleep_resource.get_sleep_log_by_date_range("2024-02-13", "invalid")


def test_get_sleep_log_by_date_range_invalid_range(sleep_resource):
    """Test that end date before start date raises InvalidDateRangeException"""
    with raises(InvalidDateRangeException):
        sleep_resource.get_sleep_log_by_date_range("2024-02-14", "2024-02-13")


def test_get_sleep_log_by_date_range_allows_today(
    sleep_resource, mock_oauth_session, mock_response_factory
):
    """Test that 'today' is accepted in date range"""
    mock_response = mock_response_factory(200, {"sleep": []})
    mock_oauth_session.request.return_value = mock_response
    sleep_resource.get_sleep_log_by_date_range("today", "today")
