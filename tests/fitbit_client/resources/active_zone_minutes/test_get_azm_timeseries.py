# tests/fitbit_client/resources/active_zone_minutes/test_get_azm_timeseries.py

"""Tests for the get_azm_timeseries endpoint."""


def test_get_azm_timeseries_with_today_date(azm_resource, mock_response_factory):
    """Test using 'today' as the date parameter"""
    expected_data = {"activities-active-zone-minutes": []}
    mock_response = mock_response_factory(200, expected_data)
    azm_resource.oauth.request.return_value = mock_response
    result = azm_resource.get_azm_timeseries_by_date(date="today")
    assert result == expected_data
    azm_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/today/1d.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
