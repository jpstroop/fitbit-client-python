# tests/resources/intraday/test_spo2_intraday.py

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException


def test_get_spo2_intraday_by_date_success(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Test successful retrieval of intraday SpO2 data"""
    expected_response = {
        "dateTime": "2024-02-13",
        "minutes": [{"minute": "00:00:00", "value": 96.5}, {"minute": "00:05:00", "value": 97.2}],
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response

    result = intraday_resource.get_spo2_intraday_by_date(date="2024-02-13")

    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/spo2/date/2024-02-13/all.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_spo2_intraday_by_interval_invalid_dates(intraday_resource):
    """Test invalid dates for SpO2 interval"""
    with raises(InvalidDateException):
        intraday_resource.get_spo2_intraday_by_interval(start_date="invalid", end_date="2024-02-14")

    with raises(InvalidDateException):
        intraday_resource.get_spo2_intraday_by_interval(start_date="2024-02-13", end_date="invalid")


def test_get_spo2_intraday_by_interval_exceeds_max_days(intraday_resource):
    """Test that exceeding 30 days raises InvalidDateRangeException"""
    with raises(InvalidDateRangeException) as exc_info:
        intraday_resource.get_spo2_intraday_by_interval(
            start_date="2024-02-13", end_date="2024-03-15"  # More than 30 days
        )

    assert "exceeds maximum allowed 30 days" in str(exc_info.value)
    assert "spo2 intraday" in str(exc_info.value)


def test_get_spo2_intraday_by_date_invalid_date(intraday_resource):
    """Test invalid date for SpO2"""
    with raises(InvalidDateException):
        intraday_resource.get_spo2_intraday_by_date(date="invalid-date")


def test_get_spo2_intraday_interval_all_endpoint(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Test SpO2 interval constructs 'all' endpoint (lines 518-519)"""
    mock_response = mock_response_factory(200, [])
    mock_oauth_session.request.return_value = mock_response

    intraday_resource.get_spo2_intraday_by_interval(start_date="2024-02-13", end_date="2024-02-14")

    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/spo2/date/2024-02-13/2024-02-14/all.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_spo2_intraday_by_date_all_endpoint(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Test SpO2 intraday endpoint with 'all' parameter"""
    mock_response = mock_response_factory(200, {"dateTime": "2024-02-13"})
    mock_oauth_session.request.return_value = mock_response

    intraday_resource.get_spo2_intraday_by_date("2024-02-13")

    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/spo2/date/2024-02-13/all.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
