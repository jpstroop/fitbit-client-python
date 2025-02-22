# tests/resources/temperature/test_get_temperature_skin_summary_by_date.py

"""Tests for the get_temperature_skin_summary_by_date endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_get_temperature_skin_summary_by_date_success(
    temperature_resource, mock_oauth_session, mock_response_factory
):
    """Test successful retrieval of skin temperature summary by date"""
    expected_response = {
        "dateTime": "2024-02-13",
        "value": {"temp": {"deviation": 0.2, "baseline": 32.5}},
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response
    result = temperature_resource.get_temperature_skin_summary_by_date("2024-02-13")
    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/temp/skin/date/2024-02-13.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_temperature_skin_summary_by_date_invalid_date(
    temperature_resource, mock_oauth_session
):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException):
        temperature_resource.get_temperature_skin_summary_by_date("invalid-date")


def test_get_temperature_skin_summary_by_date_allows_today(
    temperature_resource, mock_oauth_session, mock_response_factory
):
    """Test that 'today' is accepted as a valid date"""
    mock_response = mock_response_factory(200, {"dateTime": "today"})
    mock_oauth_session.request.return_value = mock_response
    temperature_resource.get_temperature_skin_summary_by_date("today")
