# tests/fitbit_client/resources/nutrition/test_create_water_log.py

"""Tests for the create_water_log endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.resources.constants import WaterUnit


def test_create_water_log_success(nutrition_resource, mock_response):
    """Test successful creation of a water log entry"""
    mock_response.json.return_value = {"waterLog": {"logId": 12345, "amount": 500.0}}
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.create_water_log(
        amount=500.0, date="2025-02-08", unit=WaterUnit.MILLILITERS
    )
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/foods/log/water.json",
        data=None,
        json=None,
        params={"amount": 500.0, "date": "2025-02-08", "unit": "ml"},
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_create_water_log_invalid_date(nutrition_resource):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException):
        nutrition_resource.create_water_log(amount=500.0, date="invalid-date")


def test_create_water_log_allows_today(nutrition_resource, mock_response):
    """Test that 'today' is accepted as a valid date"""
    mock_response.json.return_value = {"waterLog": {"logId": 12345}}
    mock_response.headers = {"content-type": "application/json"}
    nutrition_resource.oauth.request.return_value = mock_response
    nutrition_resource.create_water_log(amount=500.0, date="today")
