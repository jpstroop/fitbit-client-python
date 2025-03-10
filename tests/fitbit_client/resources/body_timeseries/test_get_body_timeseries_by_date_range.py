# tests/fitbit_client/resources/body_timeseries/test_get_body_timeseries_by_date_range.py

"""Tests for the get_body_timeseries_by_date_range endpoint."""

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException
from fitbit_client.resources._constants import BodyResourceType
from fitbit_client.resources._constants import MaxRanges


def test_get_body_timeseries_by_date_range_validates_dates(body_timeseries):
    """Test that invalid date formats raise InvalidDateException."""
    with raises(InvalidDateException) as exc_info:
        body_timeseries.get_body_timeseries_by_date_range(
            resource_type=BodyResourceType.BMI, begin_date="invalid-date", end_date="2023-01-01"
        )
    assert exc_info.value.field_name == "begin_date"

    with raises(InvalidDateException) as exc_info:
        body_timeseries.get_body_timeseries_by_date_range(
            resource_type=BodyResourceType.BMI, begin_date="2023-01-01", end_date="invalid-date"
        )
    assert exc_info.value.field_name == "end_date"


def test_get_body_timeseries_by_date_range_validates_order(body_timeseries):
    """Test that end date cannot be before start date."""
    with raises(InvalidDateRangeException) as exc_info:
        body_timeseries.get_body_timeseries_by_date_range(
            resource_type=BodyResourceType.BMI, begin_date="2023-02-01", end_date="2023-01-01"
        )
    assert f"Start date 2023-02-01 is after end date 2023-01-01" in str(exc_info.value)


def test_get_body_timeseries_by_date_range_max_days(body_timeseries):
    """Test maximum date range limits for each resource type."""
    test_cases = [
        (BodyResourceType.BMI, "2020-01-01", "2024-01-01", MaxRanges.GENERAL),
        (BodyResourceType.FAT, "2023-01-01", "2023-02-01", MaxRanges.BODY_FAT),
        (BodyResourceType.WEIGHT, "2023-01-01", "2023-02-02", MaxRanges.WEIGHT),
    ]
    for resource_type, begin_date, end_date, max_days in test_cases:
        with raises(InvalidDateRangeException) as exc_info:
            body_timeseries.get_body_timeseries_by_date_range(
                resource_type=resource_type, begin_date=begin_date, end_date=end_date
            )
            assert (
                f"Date range {begin_date} to {end_date} exceeds maximum allowed {max_days} days for {resource_type.value}"
                in str(exc_info.value)
            )


def test_get_body_timeseries_by_date_range_makes_correct_request(body_timeseries, mock_response):
    """Test that the correct endpoint is called with proper parameters."""
    # Set up the mock response
    body_timeseries.oauth.request.return_value = mock_response
    mock_response.json.return_value = {"expected": "response"}

    # Call the method with valid parameters that don't exceed range limits
    result = body_timeseries.get_body_timeseries_by_date_range(
        resource_type=BodyResourceType.BMI,
        begin_date="2023-01-01",
        end_date="2023-01-10",
        user_id="test_user",
        debug=False,
    )  # Well within the BMI limit

    # Assert the result
    assert result == {"expected": "response"}

    # Assert the request was made correctly
    body_timeseries.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/test_user/body/bmi/date/2023-01-01/2023-01-10.json",
        params=None,
        data=None,
        json=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
