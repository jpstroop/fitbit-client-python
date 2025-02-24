# tests/resources/intraday/test_breathingrate_intraday.py

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException


def test_get_breathing_rate_intraday_by_date_invalid_date(intraday_resource):
    """Tests invalid date for breathing rate endpoint"""
    with raises(InvalidDateException):
        intraday_resource.get_breathing_rate_intraday_by_date(date="invalid-date")


def test_get_breathing_rate_allows_today(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Tests that 'today' is accepted as a valid date"""
    mock_response = mock_response_factory(200, {"br-intraday": []})
    mock_oauth_session.request.return_value = mock_response

    # Test for single date endpoint
    intraday_resource.get_breathing_rate_intraday_by_date("today")

    # Test for interval endpoint
    intraday_resource.get_breathing_rate_intraday_by_interval(start_date="today", end_date="today")


def test_get_breathing_rate_intraday_by_interval_success(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Tests successful retrieval of breathing rate data for interval"""
    expected_response = {
        "br-intraday": [
            {
                "dateTime": "2024-02-13",
                "minutes": [
                    {"time": "00:00:00", "value": 15.2},
                    {"time": "00:01:00", "value": 15.4},
                ],
            }
        ]
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response

    result = intraday_resource.get_breathing_rate_intraday_by_interval(
        start_date="2024-02-13", end_date="2024-02-14"
    )

    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/br/date/2024-02-13/2024-02-14/all.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_breathing_rate_intraday_by_interval_invalid_dates(intraday_resource):
    """Tests invalid dates for breathing rate interval"""
    with raises(InvalidDateException):
        intraday_resource.get_breathing_rate_intraday_by_interval(
            start_date="invalid", end_date="2024-02-14"
        )

    with raises(InvalidDateException):
        intraday_resource.get_breathing_rate_intraday_by_interval(
            start_date="2024-02-13", end_date="invalid"
        )


def test_get_breathing_rate_intraday_by_interval_exceeds_max_days(intraday_resource):
    """Tests that exceeding 30 days raises InvalidDateRangeException"""
    with raises(InvalidDateRangeException) as exc_info:
        intraday_resource.get_breathing_rate_intraday_by_interval(
            start_date="2024-02-13", end_date="2024-03-15"  # More than 30 days
        )

    assert "exceeds maximum allowed 30 days" in str(exc_info.value)
    assert "breathing rate intraday" in str(exc_info.value)


def test_get_breathing_rate_interval_all_endpoint(
    intraday_resource, mock_oauth_session, mock_response_factory
):
    """Tests breathing rate interval constructs 'all' endpoint"""
    mock_response = mock_response_factory(200, {"br-intraday": []})
    mock_oauth_session.request.return_value = mock_response

    intraday_resource.get_breathing_rate_intraday_by_interval(
        start_date="2024-02-13", end_date="2024-02-14"
    )

    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/br/date/2024-02-13/2024-02-14/all.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
