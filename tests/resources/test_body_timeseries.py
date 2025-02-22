# tests/resources/test_body_timeseries.py

# Standard library imports
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.body_timeseries import BodyTimeSeriesResource
from fitbit_client.resources.constants import BodyResourceType
from fitbit_client.resources.constants import BodyTimePeriod
from fitbit_client.resources.constants import MaxRanges


class TestBodyTimeSeriesResource:
    @fixture
    def body_timeseries(self, mock_oauth_session, mock_logger):
        """Create BodyTimeSeriesResource instance"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return BodyTimeSeriesResource(mock_oauth_session, "en_US", "en_US")

    def test_get_body_timeseries_by_date_validates_date_format(self, body_timeseries):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException) as exc_info:
            body_timeseries.get_body_timeseries_by_date(
                resource_type=BodyResourceType.BMI,
                date="invalid-date",
                period=BodyTimePeriod.ONE_MONTH,
            )

        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_body_timeseries_by_date_allows_today(self, body_timeseries):
        """Test that 'today' is accepted as valid date"""
        body_timeseries._make_request = Mock()
        body_timeseries.get_body_timeseries_by_date(
            resource_type=BodyResourceType.BMI, date="today", period=BodyTimePeriod.ONE_MONTH
        )
        body_timeseries._make_request.assert_called_once()

    def test_get_body_timeseries_by_date_period_validation(self, body_timeseries):
        """Test period validation for fat/weight resources"""
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

    def test_get_body_timeseries_by_date_range_validates_dates(self, body_timeseries):
        """Test that invalid date formats raise InvalidDateException"""
        # Test invalid start date
        with raises(InvalidDateException) as exc_info:
            body_timeseries.get_body_timeseries_by_date_range(
                resource_type=BodyResourceType.BMI, begin_date="invalid-date", end_date="2023-01-01"
            )
        assert exc_info.value.field_name == "begin_date"

        # Test invalid end date
        with raises(InvalidDateException) as exc_info:
            body_timeseries.get_body_timeseries_by_date_range(
                resource_type=BodyResourceType.BMI, begin_date="2023-01-01", end_date="invalid-date"
            )
        assert exc_info.value.field_name == "end_date"

    def test_get_body_timeseries_by_date_range_validates_order(self, body_timeseries):
        """Test that end date cannot be before start date"""
        with raises(InvalidDateRangeException) as exc_info:
            body_timeseries.get_body_timeseries_by_date_range(
                resource_type=BodyResourceType.BMI, begin_date="2023-02-01", end_date="2023-01-01"
            )
        assert f"Start date 2023-02-01 is after end date 2023-01-01" in str(exc_info.value)

    def test_get_body_timeseries_by_date_range_max_days(self, body_timeseries):
        """Test maximum date range limits for each resource type"""
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

    def test_get_bodyfat_timeseries_by_date_validates_date(self, body_timeseries):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException) as exc_info:
            body_timeseries.get_bodyfat_timeseries_by_date(
                date="invalid-date", period=BodyTimePeriod.ONE_MONTH
            )
        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_weight_timeseries_by_date_validates_date(self, body_timeseries):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException) as exc_info:
            body_timeseries.get_weight_timeseries_by_date(
                date="invalid-date", period=BodyTimePeriod.ONE_MONTH
            )
        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_bodyfat_timeseries_by_date_range_validates_dates(self, body_timeseries):
        """Test that invalid dates raise InvalidDateException"""
        with raises(InvalidDateException):
            body_timeseries.get_bodyfat_timeseries_by_date_range(
                start_date="invalid-date", end_date="2023-01-01"
            )

        with raises(InvalidDateException):
            body_timeseries.get_bodyfat_timeseries_by_date_range(
                start_date="2023-01-01", end_date="invalid-date"
            )

    def test_get_weight_timeseries_by_date_range_validates_dates(self, body_timeseries):
        """Test that invalid dates raise InvalidDateException"""
        with raises(InvalidDateException):
            body_timeseries.get_weight_timeseries_by_date_range(
                start_date="invalid-date", end_date="2023-01-01"
            )

        with raises(InvalidDateException):
            body_timeseries.get_weight_timeseries_by_date_range(
                start_date="2023-01-01", end_date="invalid-date"
            )
