# tests/fitbit_client/resources/nutrition_timeseries/test_get_nutrition_timeseries_by_date.py

"""Tests for the get_nutrition_timeseries_by_date endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.resources.constants import NutritionResource
from fitbit_client.resources.constants import Period


def test_get_nutrition_timeseries_by_date_success(
    nutrition_timeseries_resource, mock_oauth_session, mock_response_factory
):
    """Test successful retrieval of nutrition data by date"""
    expected_response = {"foods-log-caloriesIn": [{"dateTime": "2024-02-13", "value": 2000}]}
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response
    result = nutrition_timeseries_resource.get_nutrition_timeseries_by_date(
        resource=NutritionResource.CALORIES_IN, date="2024-02-13", period=Period.ONE_DAY
    )
    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/foods/log/caloriesIn/date/2024-02-13/1d.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_nutrition_timeseries_by_date_invalid_date(nutrition_timeseries_resource):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException):
        nutrition_timeseries_resource.get_nutrition_timeseries_by_date(
            resource=NutritionResource.CALORIES_IN, date="invalid-date", period=Period.ONE_DAY
        )


def test_get_nutrition_timeseries_by_date_allows_today(
    nutrition_timeseries_resource, mock_oauth_session, mock_response_factory
):
    """Test that 'today' is accepted as a valid date"""
    mock_response = mock_response_factory(200, {"foods-log-caloriesIn": []})
    mock_oauth_session.request.return_value = mock_response
    nutrition_timeseries_resource.get_nutrition_timeseries_by_date(
        resource=NutritionResource.CALORIES_IN, date="today", period=Period.ONE_DAY
    )
