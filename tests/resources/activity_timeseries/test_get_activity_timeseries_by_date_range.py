# tests/resources/activity_timeseries/test_get_activity_timeseries_by_date_range.py

"""Tests for the get_activity_timeseries_by_date_range endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.constants import ActivityTimeSeriesPath


def test_get_activity_timeseries_by_date_range_success(activity_timeseries_resource, mock_response):
    """Test successful retrieval of activity time series by date range"""
    mock_response.json.return_value = {
        "activities-steps": [
            {"dateTime": "2024-02-01", "value": "10000"},
            {"dateTime": "2024-02-02", "value": "12000"},
        ]
    }
    activity_timeseries_resource.oauth.request.return_value = mock_response
    result = activity_timeseries_resource.get_activity_timeseries_by_date_range(
        resource_path=ActivityTimeSeriesPath.STEPS, start_date="2024-02-01", end_date="2024-02-02"
    )
    assert result == {
        "activities-steps": [
            {"dateTime": "2024-02-01", "value": "10000"},
            {"dateTime": "2024-02-02", "value": "12000"},
        ]
    }
    activity_timeseries_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/steps/date/2024-02-01/2024-02-02.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_activity_timeseries_by_date_range_with_user_id(
    activity_timeseries_resource, mock_response
):
    """Test getting time series by date range for a specific user"""
    mock_response.json.return_value = {"activities-steps": []}
    activity_timeseries_resource.oauth.request.return_value = mock_response
    result = activity_timeseries_resource.get_activity_timeseries_by_date_range(
        resource_path=ActivityTimeSeriesPath.STEPS,
        start_date="2024-02-01",
        end_date="2024-02-02",
        user_id="123ABC",
    )
    activity_timeseries_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/123ABC/activities/steps/date/2024-02-01/2024-02-02.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_activity_timeseries_by_date_range_invalid_dates(activity_timeseries_resource):
    """Test that invalid date formats raise InvalidDateException"""
    with raises(InvalidDateException) as exc_info:
        activity_timeseries_resource.get_activity_timeseries_by_date_range(
            resource_path=ActivityTimeSeriesPath.STEPS, start_date="invalid", end_date="2024-02-01"
        )
    assert "invalid" in str(exc_info.value)
    assert exc_info.value.field_name == "start_date"
    with raises(InvalidDateException) as exc_info:
        activity_timeseries_resource.get_activity_timeseries_by_date_range(
            resource_path=ActivityTimeSeriesPath.STEPS, start_date="2024-02-01", end_date="invalid"
        )
    assert "invalid" in str(exc_info.value)
    assert exc_info.value.field_name == "end_date"


def test_get_activity_timeseries_by_date_range_invalid_date_order(activity_timeseries_resource):
    """Test that start date after end date raises InvalidDateRangeException"""
    with raises(InvalidDateRangeException) as exc_info:
        activity_timeseries_resource.get_activity_timeseries_by_date_range(
            resource_path=ActivityTimeSeriesPath.STEPS,
            start_date="2024-02-02",
            end_date="2024-02-01",
        )
    assert f"Start date 2024-02-02 is after end date 2024-02-01" in str(exc_info.value)


def test_get_activity_timeseries_activity_calories_range_limit(
    activity_timeseries_resource, mock_response_factory
):
    """Test that activity calories respects the 30 day limit"""
    error_response = mock_response_factory(
        400,
        {
            "errors": [
                {
                    "errorType": "validation",
                    "message": "The range cannot exceed 31 days for resource type activityCalories",
                }
            ]
        },
    )
    activity_timeseries_resource.oauth.request.return_value = error_response
    with raises(ValidationException) as exc_info:
        activity_timeseries_resource.get_activity_timeseries_by_date_range(
            resource_path=ActivityTimeSeriesPath.ACTIVITY_CALORIES,
            start_date="2024-01-01",
            end_date="2024-02-15",
        )
    assert "31 days" in str(exc_info.value)
    assert "activityCalories" in str(exc_info.value)


def test_get_activity_timeseries_by_date_range_exceeds_max_range(activity_timeseries_resource):
    """Test that exceeding maximum date range raises InvalidDateRangeException"""
    with raises(InvalidDateRangeException) as exc_info:
        activity_timeseries_resource.get_activity_timeseries_by_date_range(
            resource_path=ActivityTimeSeriesPath.STEPS,
            start_date="2020-01-01",
            end_date="2024-01-01",
        )
    assert "1095 days" in str(exc_info.value)
    assert "activity time series" in str(exc_info.value)
