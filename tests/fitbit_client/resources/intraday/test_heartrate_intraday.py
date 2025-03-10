# tests/fitbit_client/resources/intraday/test_heartrate_intraday.py

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import IntradayValidationException
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.resources.constants import IntradayDetailLevel


def test_get_heartrate_intraday_by_date_success(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Tests successful retrieval of intraday heart rate data"""
    expected_response = {
        "activities-heart-intraday": {
            "dataset": [{"time": "00:00:00", "value": 65}, {"time": "00:01:00", "value": 63}],
            "datasetInterval": 1,
            "datasetType": "minute",
        }
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response

    result = intraday_resource.get_heartrate_intraday_by_date(
        date="2024-02-13", detail_level=IntradayDetailLevel.ONE_MINUTE
    )

    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/heart/date/2024-02-13/1d/1min.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_heartrate_intraday_by_date_detail_level_not_in_enum(intraday_resource):
    """Tests heart rate intraday detail level validation for non-enum values"""
    with raises(IntradayValidationException) as exc_info:
        intraday_resource.get_heartrate_intraday_by_date(
            date="2024-02-13", detail_level=object()
        )  # Not an IntradayDetailLevel

    assert exc_info.value.field_name == "detail_level"
    assert exc_info.value.resource_name == "heart rate"
    assert "Invalid detail level" in str(exc_info.value)
    assert "1sec" in exc_info.value.allowed_values
    assert "1min" in exc_info.value.allowed_values
    assert "5min" in exc_info.value.allowed_values
    assert "15min" in exc_info.value.allowed_values


def test_heartrate_intraday_by_date_with_enum_and_time_ranges(intraday_resource):
    """Tests IntradayDetailLevel enum validation for heartrate_intraday"""
    with raises(IntradayValidationException) as exc_info:
        intraday_resource.get_heartrate_intraday_by_date(date="2024-02-13", detail_level="invalid")

    assert exc_info.value.field_name == "detail_level"
    assert exc_info.value.resource_name == "heart rate"


def test_get_heartrate_intraday_by_date_with_time_range(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Tests retrieval of heart rate data with time range parameters"""
    mock_response = mock_response_factory(200, {"activities-heart-intraday": {}})
    mock_oauth_session.request.return_value = mock_response

    result = intraday_resource.get_heartrate_intraday_by_date(
        date="2024-02-13",
        detail_level=IntradayDetailLevel.ONE_MINUTE,
        start_time="09:00",
        end_time="17:00",
    )

    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/heart/date/2024-02-13/1d/1min/time/09:00/17:00.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_heartrate_intraday_interval_endpoint(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Tests endpoint construction for heart rate intraday interval"""
    mock_response = mock_response_factory(200, {})
    mock_oauth_session.request.return_value = mock_response

    result = intraday_resource.get_heartrate_intraday_by_interval(
        start_date="2024-02-13", end_date="2024-02-14", detail_level=IntradayDetailLevel.ONE_MINUTE
    )

    expected_url = "activities/heart/date/2024-02-13/2024-02-14/1min.json"
    actual_url = mock_oauth_session.request.call_args[0][1]
    assert expected_url in actual_url


def test_heartrate_intraday_interval_endpoint_construction(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Tests heart rate intraday interval endpoint construction and request"""
    mock_response = mock_response_factory(200, {})
    mock_oauth_session.request.return_value = mock_response

    intraday_resource.get_heartrate_intraday_by_interval(
        start_date="2024-02-13", end_date="2024-02-14", detail_level=IntradayDetailLevel.ONE_MINUTE
    )

    # Verify the exact endpoint construction and request
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/heart/date/2024-02-13/2024-02-14/1min.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_heartrate_intraday_interval_raises(intraday_resource):
    """Tests IntradayValidationException for invalid detail level string"""
    with raises(IntradayValidationException):
        intraday_resource.get_heartrate_intraday_by_interval(
            start_date="2024-02-13", end_date="2024-02-14", detail_level="invalid"
        )


def test_heartrate_intraday_interval_validation_exception(intraday_resource):
    """Tests heart rate intraday validation exception for invalid detail level (line 395)"""
    with raises(IntradayValidationException) as exc_info:
        intraday_resource.get_heartrate_intraday_by_interval(
            start_date="2024-02-13",
            end_date="2024-02-14",
            detail_level=IntradayDetailLevel.FIFTEEN_MINUTES,
        )  # This will trigger the exception
    assert exc_info.value.field_name == "detail_level"
    assert exc_info.value.resource_name == "heart rate"


def test_get_heartrate_intraday_by_interval_detail_level_not_in_valid_levels(intraday_resource):
    """Tests heart rate interval detail level validation against valid_levels"""
    # Using FIFTEEN_MINUTES which isn't in valid_levels for heart rate
    with raises(IntradayValidationException) as exc_info:
        intraday_resource.get_heartrate_intraday_by_interval(
            start_date="2024-02-13",
            end_date="2024-02-14",
            detail_level=IntradayDetailLevel.FIFTEEN_MINUTES,
        )

    assert exc_info.value.field_name == "detail_level"
    assert exc_info.value.resource_name == "heart rate"
    assert "Invalid detail level" in str(exc_info.value)
    assert "1sec" in exc_info.value.allowed_values
    assert "1min" in exc_info.value.allowed_values


def test_get_heartrate_intraday_by_interval_detail_level_enum(intraday_resource):
    """Tests IntradayDetailLevel enum membership validation for heart rate interval"""
    with raises(IntradayValidationException) as exc_info:
        intraday_resource.get_heartrate_intraday_by_interval(
            start_date="2024-02-13", end_date="2024-02-14", detail_level="not_in_enum"
        )

    assert exc_info.value.field_name == "detail_level"
    assert exc_info.value.resource_name == "heart rate"
    assert "Invalid detail level" in str(exc_info.value)
    assert "1sec" in exc_info.value.allowed_values
    assert "1min" in exc_info.value.allowed_values


def test_get_heartrate_intraday_by_interval_invalid_dates(intraday_resource):
    """Tests invalid date validation for heart rate interval"""
    with raises(InvalidDateException):
        intraday_resource.get_heartrate_intraday_by_interval(
            start_date="invalid", end_date="2024-02-14", detail_level=IntradayDetailLevel.ONE_MINUTE
        )

    with raises(InvalidDateException):
        intraday_resource.get_heartrate_intraday_by_interval(
            start_date="2024-02-13", end_date="invalid", detail_level=IntradayDetailLevel.ONE_MINUTE
        )
