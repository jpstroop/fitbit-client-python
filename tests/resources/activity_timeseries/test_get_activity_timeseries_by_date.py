# tests/resources/activity_timeseries/test_get_activity_timeseries_by_date.py

"""Tests for the get_activity_timeseries_by_date endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.resources.constants import ActivityTimeSeriesPath
from fitbit_client.resources.constants import Period


def test_get_activity_timeseries_by_date_success(activity_resource, mock_response):
    """Test successful retrieval of activity time series by date"""
    mock_response.json.return_value = {
        "activities-steps": [{"dateTime": "2024-02-01", "value": "10000"}]
    }
    activity_resource.oauth.request.return_value = mock_response
    result = activity_resource.get_activity_timeseries_by_date(
        resource_path=ActivityTimeSeriesPath.STEPS, date="2024-02-01", period=Period.ONE_DAY
    )
    assert result == {"activities-steps": [{"dateTime": "2024-02-01", "value": "10000"}]}
    activity_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/steps/date/2024-02-01/1d.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_activity_timeseries_by_date_with_user_id(activity_resource, mock_response):
    """Test getting time series for a specific user"""
    mock_response.json.return_value = {"activities-steps": []}
    activity_resource.oauth.request.return_value = mock_response
    result = activity_resource.get_activity_timeseries_by_date(
        resource_path=ActivityTimeSeriesPath.STEPS,
        date="2024-02-01",
        period=Period.ONE_DAY,
        user_id="123ABC",
    )
    activity_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/123ABC/activities/steps/date/2024-02-01/1d.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_activity_timeseries_by_date_invalid_date(activity_resource):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException) as exc_info:
        activity_resource.get_activity_timeseries_by_date(
            resource_path=ActivityTimeSeriesPath.STEPS, date="invalid-date", period=Period.ONE_DAY
        )
    assert "invalid-date" in str(exc_info.value)
    assert exc_info.value.field_name == "date"


"""Tests for the calories_variants endpoint."""

# Local imports


def test_calories_variants(activity_resource, mock_response):
    """Test different calorie measurement types return expected data"""
    mock_response.json.return_value = {
        "activities-activityCalories": [{"dateTime": "2024-02-01", "value": "300"}],
        "activities-calories": [{"dateTime": "2024-02-01", "value": "2000"}],
        "activities-caloriesBMR": [{"dateTime": "2024-02-01", "value": "1700"}],
    }
    activity_resource.oauth.request.return_value = mock_response
    calorie_types = [
        ActivityTimeSeriesPath.ACTIVITY_CALORIES,
        ActivityTimeSeriesPath.CALORIES,
        ActivityTimeSeriesPath.CALORIES_BMR,
        ActivityTimeSeriesPath.TRACKER_CALORIES,
        ActivityTimeSeriesPath.TRACKER_ACTIVITY_CALORIES,
    ]
    for calorie_type in calorie_types:
        result = activity_resource.get_activity_timeseries_by_date(
            resource_path=calorie_type, date="2024-02-01", period=Period.ONE_DAY
        )
        assert isinstance(result, dict)
        if result:
            for entry in next(iter(result.values())):
                assert entry["value"].isdigit()
