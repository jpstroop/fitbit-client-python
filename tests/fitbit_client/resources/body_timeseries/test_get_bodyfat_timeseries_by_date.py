# tests/fitbit_client/resources/body_timeseries/test_get_bodyfat_timeseries_by_date.py

"""Tests for the get_bodyfat_timeseries_by_date endpoint."""

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.constants import BodyTimePeriod


def test_get_bodyfat_timeseries_by_date_validates_date(body_timeseries):
    """Test that invalid date format raises InvalidDateException."""
    with raises(InvalidDateException) as exc_info:
        body_timeseries.get_bodyfat_timeseries_by_date(
            date="invalid-date", period=BodyTimePeriod.ONE_MONTH
        )
    assert exc_info.value.field_name == "date"
    assert "Invalid date format" in str(exc_info.value)


def test_get_bodyfat_timeseries_by_date_period_validation(body_timeseries):
    """Test that invalid periods raise ValidationException."""
    invalid_periods = [
        BodyTimePeriod.THREE_MONTHS,
        BodyTimePeriod.SIX_MONTHS,
        BodyTimePeriod.ONE_YEAR,
        BodyTimePeriod.MAX,
    ]
    for period in invalid_periods:
        with raises(ValidationException) as exc_info:
            body_timeseries.get_bodyfat_timeseries_by_date(date="2023-01-01", period=period)
        assert exc_info.value.field_name == "period"
        assert f"Period {period.value} not supported for body fat" in str(exc_info.value)


def test_get_bodyfat_timeseries_by_date_makes_correct_request(body_timeseries, mock_response):
    """Test that the correct endpoint is called with proper parameters."""
    # Set up the mock response
    body_timeseries.oauth.request.return_value = mock_response
    mock_response.json.return_value = {"expected": "response"}

    # Call the method
    result = body_timeseries.get_bodyfat_timeseries_by_date(
        date="2023-01-01", period=BodyTimePeriod.ONE_WEEK, user_id="test_user", debug=False
    )

    # Assert the result
    assert result == {"expected": "response"}

    # Assert the request was made correctly
    body_timeseries.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/test_user/body/log/fat/date/2023-01-01/1w.json",
        params=None,
        data=None,
        json=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
