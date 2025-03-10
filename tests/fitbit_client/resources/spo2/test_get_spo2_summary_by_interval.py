# tests/fitbit_client/resources/spo2/test_get_spo2_summary_by_interval.py

"""Tests for the get_spo2_summary_by_interval endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException


def test_get_spo2_summary_by_interval_success(
    spo2_resource, mock_oauth_session, mock_response_factory
):
    """Test successful retrieval of SpO2 summary by date range"""
    expected_response = {
        "spo2": [
            {"dateTime": "2024-02-13", "value": {"avg": 96, "min": 94, "max": 98}},
            {"dateTime": "2024-02-14", "value": {"avg": 97, "min": 95, "max": 99}},
        ]
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response
    result = spo2_resource.get_spo2_summary_by_interval(
        start_date="2024-02-13", end_date="2024-02-14"
    )
    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/spo2/date/2024-02-13/2024-02-14.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_spo2_summary_by_interval_invalid_dates(spo2_resource, mock_oauth_session):
    """Test that invalid date formats raise InvalidDateException"""
    with raises(InvalidDateException):
        spo2_resource.get_spo2_summary_by_interval(start_date="invalid", end_date="2024-02-14")
    with raises(InvalidDateException):
        spo2_resource.get_spo2_summary_by_interval(start_date="2024-02-13", end_date="invalid")


def test_get_spo2_summary_by_interval_invalid_range(spo2_resource, mock_oauth_session):
    """Test that end date before start date raises InvalidDateRangeException"""
    with raises(InvalidDateRangeException):
        spo2_resource.get_spo2_summary_by_interval(start_date="2024-02-14", end_date="2024-02-13")


def test_get_spo2_summary_by_interval_allows_today(
    spo2_resource, mock_oauth_session, mock_response_factory
):
    """Test that 'today' is accepted in date range"""
    mock_response = mock_response_factory(200, {"spo2": []})
    mock_oauth_session.request.return_value = mock_response
    spo2_resource.get_spo2_summary_by_interval("today", "today")
