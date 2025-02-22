# tests/resources/spo2/test_get_spo2_summary_by_date.py

"""Tests for the get_spo2_summary_by_date endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_get_spo2_summary_by_date_success(spo2_resource, mock_oauth_session, mock_response_factory):
    """Test successful retrieval of SpO2 summary by date"""
    expected_response = {"dateTime": "2024-02-13", "value": {"avg": 96, "min": 94, "max": 98}}
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response
    result = spo2_resource.get_spo2_summary_by_date("2024-02-13")
    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/spo2/date/2024-02-13.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_spo2_summary_by_date_invalid_date(spo2_resource, mock_oauth_session):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException):
        spo2_resource.get_spo2_summary_by_date("invalid-date")


def test_get_spo2_summary_by_date_allows_today(
    spo2_resource, mock_oauth_session, mock_response_factory
):
    """Test that 'today' is accepted as a valid date"""
    mock_response = mock_response_factory(200, {"dateTime": "today"})
    mock_oauth_session.request.return_value = mock_response
    spo2_resource.get_spo2_summary_by_date("today")
