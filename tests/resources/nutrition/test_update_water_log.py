# tests/resources/nutrition/test_update_water_log.py

"""Tests for the update_water_log endpoint."""

# Local imports

# Local imports
from fitbit_client.resources.constants import WaterUnit


def test_update_water_log_success(nutrition_resource, mock_response):
    """Test successful update of a water log entry"""
    mock_response.json.return_value = {"waterLog": {"logId": 12345, "amount": 1000.0}}
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.update_water_log(
        water_log_id=12345, amount=1000.0, unit=WaterUnit.MILLILITERS
    )
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/foods/log/water/12345.json",
        data=None,
        json=None,
        params={"amount": 1000.0, "unit": "ml"},
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_update_water_log_without_unit(nutrition_resource, mock_response):
    """Test updating water log without specifying unit (lines 733-735)"""
    mock_response.json.return_value = {"waterLog": {"logId": 12345, "amount": 1000.0}}
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.update_water_log(water_log_id=12345, amount=1000.0)
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/foods/log/water/12345.json",
        data=None,
        json=None,
        params={"amount": 1000.0},
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
