# tests/resources/test_body_timeseries.py

# Standard library imports
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.body_timeseries import BodyTimeSeriesResource
from fitbit_client.resources.constants import BodyResourceType
from fitbit_client.resources.constants import BodyTimePeriod


class TestBodyTimeSeriesResource:

    @fixture
    def body_timeseries(self, mock_oauth_session, mock_logger):
        """Create BodyTimeSeriesResource instance"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return BodyTimeSeriesResource(mock_oauth_session, "en_US", "en_US")

    def test_get_time_series_by_date_validates_date_format(self, body_timeseries):
        """Test that invalid date format raises ValidationException"""
        with raises(ValidationException) as exc_info:
            body_timeseries.get_time_series_by_date(
                resource_type=BodyResourceType.BMI,
                date="invalid-date",
                period=BodyTimePeriod.ONE_MONTH,
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_time_series_by_date_allows_today(self, body_timeseries):
        """Test that 'today' is accepted as valid date"""
        body_timeseries._make_request = Mock()
        body_timeseries.get_time_series_by_date(
            resource_type=BodyResourceType.BMI, date="today", period=BodyTimePeriod.ONE_MONTH
        )
        body_timeseries._make_request.assert_called_once()

    def test_get_time_series_by_date_range_validates_dates(self, body_timeseries):
        """Test that invalid date formats raise ValidationException"""
        # Test invalid start date
        with raises(ValidationException) as exc_info:
            body_timeseries.get_time_series_by_date_range(
                resource_type=BodyResourceType.BMI, base_date="invalid-date", end_date="2023-01-01"
            )
        assert "Invalid date format" in str(exc_info.value)
        assert exc_info.value.field_name == "date"

        # Test invalid end date
        with raises(ValidationException) as exc_info:
            body_timeseries.get_time_series_by_date_range(
                resource_type=BodyResourceType.BMI, base_date="2023-01-01", end_date="invalid-date"
            )
        assert "Invalid date format" in str(exc_info.value)

    def test_get_time_series_by_date_range_bmi_limit(self, body_timeseries):
        """Test BMI's 1095-day limit"""
        with raises(ValidationException) as exc_info:
            body_timeseries.get_time_series_by_date_range(
                resource_type=BodyResourceType.BMI,
                base_date="2020-01-01",
                end_date="2024-01-01",  # More than 1095 days
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.field_name == "date_range"
        assert "Maximum date range for bmi is 1095 days" in str(exc_info.value)

    def test_get_time_series_by_date_range_fat_limit(self, body_timeseries):
        """Test fat's 30-day limit"""
        with raises(ValidationException) as exc_info:
            body_timeseries.get_time_series_by_date_range(
                resource_type=BodyResourceType.FAT,
                base_date="2023-01-01",
                end_date="2023-02-01",  # More than 30 days
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.field_name == "date_range"
        assert "Maximum date range for fat is 30 days" in str(exc_info.value)

    def test_get_time_series_by_date_range_weight_limit(self, body_timeseries):
        """Test weight's 31-day limit"""
        with raises(ValidationException) as exc_info:
            body_timeseries.get_time_series_by_date_range(
                resource_type=BodyResourceType.WEIGHT,
                base_date="2023-01-01",
                end_date="2023-02-02",  # More than 31 days
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.field_name == "date_range"
        assert "Maximum date range for weight is 31 days" in str(exc_info.value)

    def test_get_time_series_by_date_range_valid_ranges(self, body_timeseries):
        """Test that valid ranges are accepted for each type"""
        body_timeseries._make_request = Mock()

        # Test BMI with 1000 days (under 1095 limit)
        body_timeseries.get_time_series_by_date_range(
            resource_type=BodyResourceType.BMI, base_date="2020-01-01", end_date="2022-09-27"
        )
        body_timeseries._make_request.assert_called_once()

        # Test fat with 29 days (under 30 limit)
        body_timeseries._make_request = Mock()
        body_timeseries.get_time_series_by_date_range(
            resource_type=BodyResourceType.FAT, base_date="2023-01-01", end_date="2023-01-29"
        )
        body_timeseries._make_request.assert_called_once()

        # Test weight with 30 days (under 31 limit)
        body_timeseries._make_request = Mock()
        body_timeseries.get_time_series_by_date_range(
            resource_type=BodyResourceType.WEIGHT, base_date="2023-01-01", end_date="2023-01-30"
        )
        body_timeseries._make_request.assert_called_once()

    def test_get_time_series_by_date_range_allows_today(self, body_timeseries):
        """Test that 'today' is accepted in date ranges"""
        body_timeseries._make_request = Mock()

        # Test with today as start date
        body_timeseries.get_time_series_by_date_range(
            resource_type=BodyResourceType.BMI, base_date="today", end_date="today"
        )
        body_timeseries._make_request.assert_called_once()

    def test_body_fat_time_series_by_date_uses_general_method(self, body_timeseries):
        """Test that fat-specific method uses general method with correct params"""
        body_timeseries.get_time_series_by_date = Mock()
        body_timeseries.get_body_fat_time_series_by_date(
            date="2023-01-01", period=BodyTimePeriod.ONE_MONTH
        )

        body_timeseries.get_time_series_by_date.assert_called_once_with(
            BodyResourceType.FAT, "2023-01-01", BodyTimePeriod.ONE_MONTH, "-"
        )

    def test_body_fat_time_series_by_date_range_uses_general_method(self, body_timeseries):
        """Test that fat-specific range method uses general method with correct params"""
        body_timeseries.get_time_series_by_date_range = Mock()
        body_timeseries.get_body_fat_time_series_by_date_range(
            base_date="2023-01-01", end_date="2023-01-15"
        )

        body_timeseries.get_time_series_by_date_range.assert_called_once_with(
            BodyResourceType.FAT, "2023-01-01", "2023-01-15", "-"
        )

    def test_weight_time_series_by_date_uses_general_method(self, body_timeseries):
        """Test that weight-specific method uses general method with correct params"""
        body_timeseries.get_time_series_by_date = Mock()
        body_timeseries.get_weight_time_series_by_date(
            date="2023-01-01", period=BodyTimePeriod.ONE_MONTH
        )

        body_timeseries.get_time_series_by_date.assert_called_once_with(
            BodyResourceType.WEIGHT, "2023-01-01", BodyTimePeriod.ONE_MONTH, "-"
        )

    def test_weight_time_series_by_date_range_uses_general_method(self, body_timeseries):
        """Test that weight-specific range method uses general method with correct params"""
        body_timeseries.get_time_series_by_date_range = Mock()
        body_timeseries.get_weight_time_series_by_date_range(
            base_date="2023-01-01", end_date="2023-01-15"
        )

        body_timeseries.get_time_series_by_date_range.assert_called_once_with(
            BodyResourceType.WEIGHT, "2023-01-01", "2023-01-15", "-"
        )
