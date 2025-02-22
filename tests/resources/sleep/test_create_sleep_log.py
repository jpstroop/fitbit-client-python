# tests/resources/sleep/test_create_sleep_log.py

"""Tests for the create_sleep_log endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_create_sleep_log_success(sleep_resource, mock_oauth_session, mock_response_factory):
    """Test successful creation of sleep log entry"""
    expected_response = {"sleep": [{"logId": 123, "startTime": "22:00", "duration": 28800000}]}
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response
    result = sleep_resource.create_sleep_log(
        start_time="22:00", duration_millis=28800000, date="2024-02-13"
    )
    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1.2/user/-/sleep.json",
        data=None,
        json=None,
        params={"startTime": "22:00", "duration": 28800000, "date": "2024-02-13"},
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_create_sleep_log_invalid_duration(sleep_resource):
    """Test that negative duration raises ValueError"""
    with raises(ValueError) as exc_info:
        sleep_resource.create_sleep_log(start_time="22:00", duration_millis=-1, date="2024-02-13")
    assert "duration_millis must be positive" in str(exc_info.value)


def test_create_sleep_log_invalid_date(sleep_resource):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException):
        sleep_resource.create_sleep_log(
            start_time="22:00", duration_millis=28800000, date="invalid-date"
        )


def test_create_sleep_log_allows_today(sleep_resource, mock_oauth_session, mock_response_factory):
    """Test that 'today' is accepted as a valid date"""
    mock_response = mock_response_factory(200, {"sleep": [{"logId": 123}]})
    mock_oauth_session.request.return_value = mock_response
    sleep_resource.create_sleep_log(start_time="22:00", duration_millis=28800000, date="today")
