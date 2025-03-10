# tests/fitbit_client/resources/nutrition/test_get_food_log.py

"""Tests for the get_food_log endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_get_food_log_success(nutrition_resource, mock_response_factory):
    """Test successful retrieval of food log entries"""
    mock_response = mock_response_factory(
        200,
        {
            "foods": [{"logId": 12345, "loggedFood": {"foodId": 67890, "amount": 100.0}}],
            "summary": {"calories": 500},
        },
    )
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.get_food_log(date="2025-02-08")
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/foods/log/date/2025-02-08.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_food_log_invalid_date(nutrition_resource):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException):
        nutrition_resource.get_food_log("invalid-date")


def test_get_food_log_allows_today(nutrition_resource, mock_response_factory):
    """Test that 'today' is accepted as a valid date"""
    mock_response = mock_response_factory(200, {"foods": []})
    nutrition_resource.oauth.request.return_value = mock_response
    nutrition_resource.get_food_log("today")
