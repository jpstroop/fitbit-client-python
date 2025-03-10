# tests/fitbit_client/resources/body_timeseries/test_get_body_timeseries_by_date.py

"""Tests for the get_body_timeseries_by_date endpoint."""

# Standard library imports
from unittest.mock import Mock

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources._constants import BodyResourceType
from fitbit_client.resources._constants import BodyTimePeriod


def test_get_body_timeseries_by_date_validates_date_format(body_timeseries):
    """Test that invalid date format raises InvalidDateException."""
    with raises(InvalidDateException) as exc_info:
        body_timeseries.get_body_timeseries_by_date(
            resource_type=BodyResourceType.BMI, date="invalid-date", period=BodyTimePeriod.ONE_MONTH
        )
    assert exc_info.value.field_name == "date"
    assert "Invalid date format" in str(exc_info.value)


def test_get_body_timeseries_by_date_allows_today(body_timeseries):
    """Test that 'today' is accepted as valid date."""
    body_timeseries._make_request = Mock()
    body_timeseries.get_body_timeseries_by_date(
        resource_type=BodyResourceType.BMI, date="today", period=BodyTimePeriod.ONE_MONTH
    )
    body_timeseries._make_request.assert_called_once()


def test_get_body_timeseries_by_date_period_validation(body_timeseries):
    """Test period validation for fat/weight resources."""
    invalid_periods = [
        BodyTimePeriod.THREE_MONTHS,
        BodyTimePeriod.SIX_MONTHS,
        BodyTimePeriod.ONE_YEAR,
        BodyTimePeriod.MAX,
    ]
    for resource_type in (BodyResourceType.FAT, BodyResourceType.WEIGHT):
        for period in invalid_periods:
            with raises(ValidationException) as exc_info:
                body_timeseries.get_body_timeseries_by_date(
                    resource_type=resource_type, date="2023-01-01", period=period
                )
            assert exc_info.value.field_name == "period"
            assert f"Period {period.value} not supported for {resource_type.value}" in str(
                exc_info.value
            )


def test_get_body_timeseries_by_date_successful_flow(body_timeseries, mock_response):
    """Test the successful flow through validation and request for get_body_timeseries_by_date."""
    # Set up the mock response
    body_timeseries.oauth.request.return_value = mock_response
    mock_response.json.return_value = {"expected": "response"}

    # Test with BMI resource type (which allows all periods)
    result = body_timeseries.get_body_timeseries_by_date(
        resource_type=BodyResourceType.BMI,
        date="2023-01-01",
        period=BodyTimePeriod.THREE_MONTHS,
        user_id="test_user",
        debug=False,
    )  # Use a period that would be restricted for other resources

    # Assert the result
    assert result == {"expected": "response"}

    # Assert the request was made correctly
    body_timeseries.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/test_user/body/bmi/date/2023-01-01/3m.json",
        params=None,
        data=None,
        json=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )

    # Test with FAT resource type using an allowed period
    body_timeseries.oauth.request.reset_mock()
    result = body_timeseries.get_body_timeseries_by_date(
        resource_type=BodyResourceType.FAT,
        date="2023-01-01",
        period=BodyTimePeriod.ONE_WEEK,
        user_id="test_user",
        debug=False,
    )  # Use a period that is allowed for fat

    # Assert the request was made correctly
    body_timeseries.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/test_user/body/fat/date/2023-01-01/1w.json",
        params=None,
        data=None,
        json=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_body_timeseries_by_date_makes_correct_request(body_timeseries, mock_response):
    """Test that the correct endpoint is called with proper parameters."""
    # Set up the mock response
    body_timeseries.oauth.request.return_value = mock_response
    mock_response.json.return_value = {"expected": "response"}

    # Call the method
    result = body_timeseries.get_body_timeseries_by_date(
        resource_type=BodyResourceType.BMI,
        date="2023-01-01",
        period=BodyTimePeriod.ONE_MONTH,
        user_id="test_user",
        debug=False,
    )

    # Assert the result
    assert result == {"expected": "response"}

    # Assert the request was made correctly
    body_timeseries.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/test_user/body/bmi/date/2023-01-01/1m.json",
        params=None,
        data=None,
        json=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
