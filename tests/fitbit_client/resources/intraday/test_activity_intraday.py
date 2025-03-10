# tests/fitbit_client/resources/intraday/test_activity_intraday.py

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import IntradayValidationException
from fitbit_client.resources.constants import IntradayDetailLevel


def test_get_activity_intraday_by_date_success(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Tests successful retrieval of intraday activity data"""
    expected_response = {
        "activities-steps-intraday": {
            "dataset": [{"time": "00:00:00", "value": 0}, {"time": "00:01:00", "value": 5}],
            "datasetInterval": 1,
            "datasetType": "minute",
        }
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response

    result = intraday_resource.get_activity_intraday_by_date(
        date="2024-02-13", resource_path="steps", detail_level=IntradayDetailLevel.ONE_MINUTE
    )

    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/steps/date/2024-02-13/1d/1min.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_activity_intraday_by_date_invalid_resource(intraday_resource):
    """Tests that invalid resource_path raises IntradayValidationException"""
    with raises(IntradayValidationException) as exc_info:
        intraday_resource.get_activity_intraday_by_date(
            date="2024-02-13", resource_path="invalid", detail_level=IntradayDetailLevel.ONE_MINUTE
        )

    assert exc_info.value.field_name == "resource_path"
    assert exc_info.value.resource_name == "activity"
    assert "Invalid resource path" in str(exc_info.value)


def test_activity_intraday_by_date_invalid_detail_level(intraday_resource):
    """Tests activity intraday detail level validation exception"""
    with raises(IntradayValidationException) as exc_info:
        intraday_resource.get_activity_intraday_by_date(
            date="2024-02-13", resource_path="steps", detail_level="invalid_level"
        )

    assert exc_info.value.field_name == "detail_level"
    assert exc_info.value.resource_name == "activity"
    assert "Invalid detail level" in str(exc_info.value)
    assert "1min" in exc_info.value.allowed_values
    assert "5min" in exc_info.value.allowed_values
    assert "15min" in exc_info.value.allowed_values


def test_activity_intraday_by_date_with_time_range(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Tests activity intraday time range endpoint construction"""
    mock_response = mock_response_factory(200, {})
    mock_oauth_session.request.return_value = mock_response

    intraday_resource.get_activity_intraday_by_date(
        date="2024-02-13",
        resource_path="steps",
        detail_level=IntradayDetailLevel.ONE_MINUTE,
        start_time="09:00",
        end_time="10:00",
    )

    mock_oauth_session.request.assert_called_once()
    url = mock_oauth_session.request.call_args[0][1]
    assert "time/09:00/10:00" in url


def test_get_activity_intraday_by_interval_success(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Tests successful retrieval of activity data for interval"""
    expected_response = {
        "activities-steps-intraday": [
            {
                "dateTime": "2024-02-13",
                "dataset": [{"time": "00:00:00", "value": 0}, {"time": "00:01:00", "value": 5}],
            }
        ]
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response

    result = intraday_resource.get_activity_intraday_by_interval(
        start_date="2024-02-13",
        end_date="2024-02-14",
        resource_path="steps",
        detail_level=IntradayDetailLevel.ONE_MINUTE,
    )

    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/steps/date/2024-02-13/2024-02-14/1min.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_activity_intraday_by_interval_invalid_resource(intraday_resource):
    """Tests invalid resource path for activity interval"""
    with raises(IntradayValidationException) as exc_info:
        intraday_resource.get_activity_intraday_by_interval(
            start_date="2024-02-13",
            end_date="2024-02-14",
            resource_path="invalid",
            detail_level=IntradayDetailLevel.ONE_MINUTE,
        )

    assert exc_info.value.field_name == "resource_path"
    assert exc_info.value.resource_name == "activity"
    assert "Invalid resource path" in str(exc_info.value)


def test_activity_intraday_interval_raises_validation_exception(intraday_resource):
    """Tests activity intraday resource path validation (line 218)"""
    with raises(IntradayValidationException) as exc_info:
        intraday_resource.get_activity_intraday_by_interval(
            start_date="2024-02-13",
            end_date="2024-02-14",
            resource_path="invalid",
            detail_level=IntradayDetailLevel.ONE_MINUTE,
        )  # This will trigger the exception
    assert exc_info.value.field_name == "resource_path"
    assert exc_info.value.resource_name == "activity"


def test_get_activity_intraday_by_interval_invalid_detail_level(intraday_resource):
    """Tests invalid detail level for activity interval"""
    with raises(IntradayValidationException) as exc_info:
        intraday_resource.get_activity_intraday_by_interval(
            start_date="2024-02-13",
            end_date="2024-02-14",
            resource_path="steps",
            detail_level="invalid",
        )

    assert exc_info.value.field_name == "detail_level"
    assert exc_info.value.resource_name == "activity"
    assert "Invalid detail level" in str(exc_info.value)


def test_activity_intraday_interval_detail_level_raises(intraday_resource):
    """Tests IntradayValidationException for invalid detail level"""
    with raises(IntradayValidationException):
        intraday_resource.get_activity_intraday_by_interval(
            start_date="2024-02-13",
            end_date="2024-02-14",
            resource_path="steps",
            detail_level="invalid",
        )


def test_get_activity_intraday_by_interval_detail_level_not_in_enum(intraday_resource):
    """Tests IntradayDetailLevel enum check for activity interval"""
    with raises(IntradayValidationException) as exc_info:
        intraday_resource.get_activity_intraday_by_interval(
            start_date="2024-02-13",
            end_date="2024-02-14",
            resource_path="steps",
            detail_level=object(),
        )  # Not an IntradayDetailLevel

    assert exc_info.value.field_name == "detail_level"
    assert exc_info.value.resource_name == "activity"
    assert "Invalid detail level" in str(exc_info.value)


def test_get_activity_intraday_by_interval_detail_level_membership(intraday_resource):
    """Tests IntradayDetailLevel membership validation for activity interval"""
    with raises(IntradayValidationException) as exc_info:
        intraday_resource.get_activity_intraday_by_interval(
            start_date="2024-02-13",
            end_date="2024-02-14",
            resource_path="steps",
            detail_level="not_a_member",
        )

    assert exc_info.value.field_name == "detail_level"
    assert exc_info.value.resource_name == "activity"
    assert "Invalid detail level" in str(exc_info.value)


def test_get_activity_intraday_by_interval_with_time_range(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Tests retrieval of activity data for interval with time range"""
    mock_response = mock_response_factory(200, {"activities-steps-intraday": {}})
    mock_oauth_session.request.return_value = mock_response

    result = intraday_resource.get_activity_intraday_by_interval(
        start_date="2024-02-13",
        end_date="2024-02-13",
        resource_path="steps",
        detail_level=IntradayDetailLevel.ONE_MINUTE,
        start_time="09:00",
        end_time="17:00",
    )

    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/steps/date/2024-02-13/2024-02-13/1min/time/09:00/17:00.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_activity_intraday_interval_with_time(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Tests endpoint time concatenation in get_activity_intraday_by_interval"""
    mock_response = mock_response_factory(200, {})
    mock_oauth_session.request.return_value = mock_response

    intraday_resource.get_activity_intraday_by_interval(
        start_date="2024-02-13",
        end_date="2024-02-14",
        resource_path="steps",
        detail_level=IntradayDetailLevel.ONE_MINUTE,
        start_time="09:00",
        end_time="10:00",
    )

    expected_url = "activities/steps/date/2024-02-13/2024-02-14/1min/time/09:00/10:00.json"
    actual_url = mock_oauth_session.request.call_args[0][1]
    assert expected_url in actual_url


def test_activity_intraday_interval_adds_time_range(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Tests activity intraday time range endpoint construction (line 227)"""
    mock_response = mock_response_factory(200, {})
    mock_oauth_session.request.return_value = mock_response

    intraday_resource.get_activity_intraday_by_interval(
        start_date="2024-02-13",
        end_date="2024-02-14",
        resource_path="steps",
        detail_level=IntradayDetailLevel.ONE_MINUTE,
        start_time="09:00",
        end_time="10:00",
    )

    # Verify the URL includes the time range
    mock_oauth_session.request.assert_called_once()
    url = mock_oauth_session.request.call_args[0][1]
    assert "time/09:00/10:00" in url
