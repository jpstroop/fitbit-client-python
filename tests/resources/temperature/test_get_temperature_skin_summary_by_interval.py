# tests/resources/temperature/test_get_temperature_skin_summary_by_interval.py

"""Tests for the get_temperature_skin_summary_by_interval endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException


def test_get_temperature_skin_summary_by_interval_success(
    temperature_resource, mock_oauth_session, mock_response_factory
):
    """Test successful retrieval of skin temperature summary by date range"""
    expected_response = {
        "temp-skin": [
            {"dateTime": "2024-02-13", "value": {"temp": {"deviation": 0.2, "baseline": 32.5}}},
            {"dateTime": "2024-02-14", "value": {"temp": {"deviation": 0.1, "baseline": 32.5}}},
        ]
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response
    result = temperature_resource.get_temperature_skin_summary_by_interval(
        start_date="2024-02-13", end_date="2024-02-14"
    )
    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/temp/skin/date/2024-02-13/2024-02-14.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_temperature_skin_summary_by_interval_exceeds_max_days(
    temperature_resource, mock_oauth_session
):
    """Test that exceeding 30 days raises InvalidDateRangeException"""
    with raises(InvalidDateRangeException) as exc_info:
        temperature_resource.get_temperature_skin_summary_by_interval(
            start_date="2024-02-13", end_date="2024-03-15"
        )
    assert "Date range 2024-02-13 to 2024-03-15 exceeds maximum allowed 30 days" in str(
        exc_info.value
    )


def test_get_temperature_skin_summary_by_interval_invalid_dates(
    temperature_resource, mock_oauth_session
):
    """Test that invalid date formats raise InvalidDateException"""
    with raises(InvalidDateException):
        temperature_resource.get_temperature_skin_summary_by_interval(
            start_date="invalid", end_date="2024-02-14"
        )
    with raises(InvalidDateException):
        temperature_resource.get_temperature_skin_summary_by_interval(
            start_date="2024-02-13", end_date="invalid"
        )


def test_get_temperature_skin_summary_by_interval_invalid_range(
    temperature_resource, mock_oauth_session
):
    """Test that end date before start date raises InvalidDateRangeException"""
    with raises(InvalidDateRangeException):
        temperature_resource.get_temperature_skin_summary_by_interval(
            start_date="2024-02-14", end_date="2024-02-13"
        )


def test_get_temperature_skin_summary_by_interval_allows_today(
    temperature_resource, mock_oauth_session, mock_response_factory
):
    """Test that 'today' is accepted in date range"""
    mock_response = mock_response_factory(200, {"temp-skin": []})
    mock_oauth_session.request.return_value = mock_response
    temperature_resource.get_temperature_skin_summary_by_interval("today", "today")
