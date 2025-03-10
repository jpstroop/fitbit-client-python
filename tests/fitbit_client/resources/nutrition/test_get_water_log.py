# tests/fitbit_client/resources/nutrition/test_get_water_log.py

"""Tests for the get_water_log endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_get_water_log_success(nutrition_resource, mock_response):
    """Test successful retrieval of water log entries"""
    mock_response.json.return_value = {
        "water": [{"logId": 12345, "amount": 500.0}],
        "summary": {"water": 500.0},
    }
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.get_water_log(date="2025-02-08")
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/foods/log/water/date/2025-02-08.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_water_log_invalid_date(nutrition_resource):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException):
        nutrition_resource.get_water_log("invalid-date")


def test_get_water_log_allows_today(nutrition_resource, mock_response):
    """Test that 'today' is accepted as a valid date"""
    mock_response.json.return_value = {"water": []}
    mock_response.headers = {"content-type": "application/json"}
    nutrition_resource.oauth.request.return_value = mock_response
    nutrition_resource.get_water_log("today")
