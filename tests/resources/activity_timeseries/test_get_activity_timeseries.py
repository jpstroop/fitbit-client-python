# tests/resources/activity_timeseries/test_get_activity_timeseries.py

"""Tests for the get_activity_timeseries endpoint."""

# Local imports

# Local imports
from fitbit_client.resources.constants import ActivityTimeSeriesPath
from fitbit_client.resources.constants import Period


def test_get_activity_timeseries_with_today_date(activity_resource, mock_response):
    """Test using 'today' as the date parameter"""
    mock_response.json.return_value = {"activities-steps": []}
    activity_resource.oauth.request.return_value = mock_response
    result = activity_resource.get_activity_timeseries_by_date(
        resource_path=ActivityTimeSeriesPath.STEPS, date="today", period=Period.ONE_DAY
    )
    activity_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/steps/date/today/1d.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_activity_timeseries_different_periods(activity_resource, mock_response):
    """Test getting time series with different period values"""
    mock_response.json.return_value = {"activities-steps": []}
    activity_resource.oauth.request.return_value = mock_response
    periods = [
        Period.ONE_DAY,
        Period.SEVEN_DAYS,
        Period.THIRTY_DAYS,
        Period.ONE_WEEK,
        Period.ONE_MONTH,
        Period.THREE_MONTHS,
        Period.SIX_MONTHS,
        Period.ONE_YEAR,
        Period.MAX,
    ]
    for period in periods:
        activity_resource.get_activity_timeseries_by_date(
            resource_path=ActivityTimeSeriesPath.STEPS, date="2024-02-01", period=period
        )
        expected_url = (
            f"https://api.fitbit.com/1/user/-/activities/steps/date/2024-02-01/{period.value}.json"
        )
        last_call = activity_resource.oauth.request.call_args_list[-1]
        assert last_call[0][1] == expected_url
