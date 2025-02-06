# tests/resources/test_intraday/test_azm_intraday.py

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import IntradayValidationException
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException
from fitbit_client.resources.constants import IntradayDetailLevel


def test_get_azm_intraday_by_date_success(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Test successful retrieval of intraday AZM data"""
    expected_response = {
        "activities-active-zone-minutes-intraday": {
            "dataset": [
                {
                    "time": "00:00:00",
                    "value": {
                        "fatBurnActiveZoneMinutes": 1,
                        "cardioActiveZoneMinutes": 0,
                        "peakActiveZoneMinutes": 0,
                        "activeZoneMinutes": 1,
                    },
                }
            ],
            "datasetInterval": 1,
            "datasetType": "minute",
        }
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response

    result = intraday_resource.get_azm_intraday_by_date(
        date="2024-02-13", detail_level=IntradayDetailLevel.ONE_MINUTE
    )

    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/2024-02-13/1d/1min.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_azm_intraday_by_date_with_time_range(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Test retrieval of intraday AZM data with time range"""
    mock_response = mock_response_factory(200, {"activities-active-zone-minutes-intraday": {}})
    mock_oauth_session.request.return_value = mock_response

    result = intraday_resource.get_azm_intraday_by_date(
        date="2024-02-13",
        detail_level=IntradayDetailLevel.ONE_MINUTE,
        start_time="08:00",
        end_time="09:00",
    )

    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/2024-02-13/1d/1min/time/08:00/09:00.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_azm_intraday_by_date_invalid_detail_level(intraday_resource):
    """Test that invalid detail_level raises IntradayValidationException"""
    with raises(IntradayValidationException) as exc_info:
        intraday_resource.get_azm_intraday_by_date(date="2024-02-13", detail_level="invalid")

    assert exc_info.value.field_name == "detail_level"
    assert exc_info.value.resource_name == "active zone minutes"
    assert "Invalid detail level" in str(exc_info.value)


def test_get_azm_intraday_by_date_invalid_date(intraday_resource):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException):
        intraday_resource.get_azm_intraday_by_date(
            date="invalid-date", detail_level=IntradayDetailLevel.ONE_MINUTE
        )


def test_get_azm_intraday_by_interval_success(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Test successful retrieval of intraday AZM data for interval"""
    expected_response = {
        "activities-active-zone-minutes-intraday": [
            {
                "dateTime": "2024-02-13",
                "minutes": [
                    {
                        "time": "00:00:00",
                        "value": {
                            "fatBurnActiveZoneMinutes": 1,
                            "cardioActiveZoneMinutes": 0,
                            "peakActiveZoneMinutes": 0,
                            "activeZoneMinutes": 1,
                        },
                    }
                ],
            }
        ]
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response

    result = intraday_resource.get_azm_intraday_by_interval(
        start_date="2024-02-13", end_date="2024-02-13", detail_level=IntradayDetailLevel.ONE_MINUTE
    )

    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/2024-02-13/2024-02-13/1min.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_azm_intraday_by_interval_exceeds_max_days(intraday_resource):
    """Test that exceeding max days raises InvalidDateRangeException"""
    with raises(InvalidDateRangeException) as exc_info:
        intraday_resource.get_azm_intraday_by_interval(
            start_date="2024-02-13",
            end_date="2024-02-15",  # More than 24 hours
            detail_level=IntradayDetailLevel.ONE_MINUTE,
        )

    assert "exceeds maximum allowed" in str(exc_info.value)
    assert "active zone minutes intraday" in str(exc_info.value)


def test_get_azm_intraday_by_interval_with_time_range(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Test retrieval of AZM data for interval with time range"""
    mock_response = mock_response_factory(200, {"activities-active-zone-minutes-intraday": {}})
    mock_oauth_session.request.return_value = mock_response

    intraday_resource.get_azm_intraday_by_interval(
        start_date="2024-02-13",
        end_date="2024-02-13",
        detail_level=IntradayDetailLevel.ONE_MINUTE,
        start_time="08:00",
        end_time="09:00",
    )

    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/2024-02-13/2024-02-13/1min/time/08:00/09:00.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_azm_intraday_by_interval_detail_level_validation(intraday_resource):
    """Test detail level validation for AZM interval"""
    with raises(IntradayValidationException) as exc_info:
        intraday_resource.get_azm_intraday_by_interval(
            start_date="2024-02-13", end_date="2024-02-14", detail_level="invalid"
        )

    assert exc_info.value.field_name == "detail_level"
    assert exc_info.value.resource_name == "active zone minutes"
    assert "Invalid detail level" in str(exc_info.value)
    valid_levels = [
        IntradayDetailLevel.ONE_MINUTE,
        IntradayDetailLevel.FIVE_MINUTES,
        IntradayDetailLevel.FIFTEEN_MINUTES,
    ]
    assert all(level.value in exc_info.value.allowed_values for level in valid_levels)
