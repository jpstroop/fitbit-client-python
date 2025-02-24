# tests/resources/body_timeseries/test_get_weight_timeseries_by_date_range.py

"""Tests for the get_weight_timeseries_by_date_range endpoint."""

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException


def test_get_weight_timeseries_by_date_range_validates_dates(body_timeseries):
    """Test that invalid dates raise InvalidDateException."""
    with raises(InvalidDateException):
        body_timeseries.get_weight_timeseries_by_date_range(
            start_date="invalid-date", end_date="2023-01-01"
        )
    with raises(InvalidDateException):
        body_timeseries.get_weight_timeseries_by_date_range(
            start_date="2023-01-01", end_date="invalid-date"
        )


def test_get_weight_timeseries_by_date_range_validates_order(body_timeseries):
    """Test that end date cannot be before start date."""
    with raises(InvalidDateRangeException) as exc_info:
        body_timeseries.get_weight_timeseries_by_date_range(
            start_date="2023-02-01", end_date="2023-01-01"
        )
    assert "Start date 2023-02-01 is after end date 2023-01-01" in str(exc_info.value)


def test_get_weight_timeseries_by_date_range_max_days(body_timeseries):
    """Test maximum date range limit for weight."""
    with raises(InvalidDateRangeException) as exc_info:
        body_timeseries.get_weight_timeseries_by_date_range(
            start_date="2023-01-01", end_date="2023-02-02"  # 32 days, exceeds 31 day limit
        )
    # The MaxRanges enum is displayed in the error message, not its value
    assert "exceeds maximum allowed" in str(exc_info.value)
    assert "weight" in str(exc_info.value)


def test_get_weight_timeseries_by_date_range_makes_correct_request(body_timeseries, mock_response):
    """Test that the correct endpoint is called with proper parameters."""
    # Set up the mock response
    body_timeseries.oauth.request.return_value = mock_response
    mock_response.json.return_value = {"expected": "response"}

    # Call the method with a valid date range (under 31 days)
    result = body_timeseries.get_weight_timeseries_by_date_range(
        start_date="2023-01-01", end_date="2023-01-10", user_id="test_user", debug=False
    )

    # Assert the result
    assert result == {"expected": "response"}

    # Assert the request was made correctly
    body_timeseries.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/test_user/body/log/weight/date/2023-01-01/2023-01-10.json",
        params=None,
        data=None,
        json=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
