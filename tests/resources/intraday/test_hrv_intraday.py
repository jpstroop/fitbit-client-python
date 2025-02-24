# tests/resources/intraday/test_hrv_intraday.py

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException


def test_get_hrv_intraday_by_date_success(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Tests successful retrieval of intraday HRV data"""
    expected_response = {
        "hrv": [
            {
                "dateTime": "2024-02-13",
                "minutes": [
                    {
                        "minute": "00:00:00",
                        "value": {"rmssd": 45.5, "coverage": 98.5, "hf": 725.9, "lf": 1355.7},
                    }
                ],
            }
        ]
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response

    result = intraday_resource.get_hrv_intraday_by_date(date="2024-02-13")

    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/hrv/date/2024-02-13/all.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_hrv_intraday_by_date_invalid_date(intraday_resource):
    """Tests invalid date validation for HRV endpoint"""
    with raises(InvalidDateException):
        intraday_resource.get_hrv_intraday_by_date(date="invalid-date")


def test_get_hrv_intraday_by_date_all_endpoint(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Tests HRV intraday endpoint with 'all' parameter construction"""
    mock_response = mock_response_factory(200, {"hrv": []})
    mock_oauth_session.request.return_value = mock_response

    intraday_resource.get_hrv_intraday_by_date("2024-02-13")

    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/hrv/date/2024-02-13/all.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_hrv_intraday_interval_all_endpoint(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Tests HRV interval 'all' endpoint construction"""
    mock_response = mock_response_factory(200, {"hrv": []})
    mock_oauth_session.request.return_value = mock_response

    intraday_resource.get_hrv_intraday_by_interval(start_date="2024-02-13", end_date="2024-02-14")

    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/hrv/date/2024-02-13/2024-02-14/all.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_hrv_intraday_by_interval_invalid_dates(intraday_resource):
    """Tests invalid date validation for HRV interval"""
    with raises(InvalidDateException):
        intraday_resource.get_hrv_intraday_by_interval(start_date="invalid", end_date="2024-02-14")

    with raises(InvalidDateException):
        intraday_resource.get_hrv_intraday_by_interval(start_date="2024-02-13", end_date="invalid")


def test_get_hrv_intraday_by_date_range_validation(intraday_resource):
    """Tests date range validation for HRV intraday"""
    # Test invalid start date
    with raises(InvalidDateException) as exc_info:
        intraday_resource.get_hrv_intraday_by_interval(
            start_date="invalid-start", end_date="2024-02-14"
        )
    assert "Invalid date format" in str(exc_info.value)
    assert exc_info.value.date_str == "invalid-start"

    # Test date range exceeds max
    with raises(InvalidDateRangeException) as exc_info:
        intraday_resource.get_hrv_intraday_by_interval(
            start_date="2024-02-13", end_date="2024-03-15"  # More than 30 days
        )
    assert "exceeds maximum allowed 30 days" in str(exc_info.value)
    assert "heart rate variability intraday" in str(exc_info.value)
