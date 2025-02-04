# tests/resources/test_nutrition_timeseries.py

# Standard library imports
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.constants import NutritionResource
from fitbit_client.resources.constants import Period
from fitbit_client.resources.nutrition_timeseries import NutritionTimeSeriesResource


class TestNutritionTimeSeriesResource:

    @fixture
    def nutrition_timeseries(self, mock_oauth_session, mock_logger):
        """Create NutritionTimeSeriesResource instance"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return NutritionTimeSeriesResource(mock_oauth_session, "en_US", "en_US")

    def test_get_time_series_by_date_validates_date_format(self, nutrition_timeseries):
        """Test that invalid date format raises ValidationException"""
        with raises(ValidationException) as exc_info:
            nutrition_timeseries.get_time_series_by_date(
                resource=NutritionResource.CALORIES_IN, date="invalid-date", period=Period.ONE_MONTH
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_time_series_by_date_allows_today(self, nutrition_timeseries):
        """Test that 'today' is accepted as a valid date"""
        nutrition_timeseries._make_request = Mock()
        nutrition_timeseries.get_time_series_by_date(
            resource=NutritionResource.CALORIES_IN, date="today", period=Period.ONE_MONTH
        )
        nutrition_timeseries._make_request.assert_called_once()

    def test_get_time_series_by_date_range_validates_start_date(self, nutrition_timeseries):
        """Test that invalid start date raises ValidationException"""
        with raises(ValidationException) as exc_info:
            nutrition_timeseries.get_time_series_by_date_range(
                resource=NutritionResource.CALORIES_IN,
                start_date="invalid-date",
                end_date="2023-01-01",
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_time_series_by_date_range_validates_end_date(self, nutrition_timeseries):
        """Test that invalid end date raises ValidationException"""
        with raises(ValidationException) as exc_info:
            nutrition_timeseries.get_time_series_by_date_range(
                resource=NutritionResource.CALORIES_IN,
                start_date="2023-01-01",
                end_date="invalid-date",
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_time_series_by_date_range_validates_max_range(self, nutrition_timeseries):
        """Test that exceeding 1095-day range limit raises ValidationException"""
        with raises(ValidationException) as exc_info:
            nutrition_timeseries.get_time_series_by_date_range(
                resource=NutritionResource.CALORIES_IN,
                start_date="2020-01-01",
                end_date="2024-01-01",  # More than 1095 days
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "date_range"
        assert "Maximum date range is 1095 days" in str(exc_info.value)

    def test_get_time_series_by_date_range_allows_valid_range(self, nutrition_timeseries):
        """Test that valid date range is accepted"""
        nutrition_timeseries._make_request = Mock()
        nutrition_timeseries.get_time_series_by_date_range(
            resource=NutritionResource.CALORIES_IN,
            start_date="2023-01-01",
            end_date="2023-12-31",  # Less than 1095 days
        )
        nutrition_timeseries._make_request.assert_called_once()

    def test_get_time_series_by_date_range_allows_today(self, nutrition_timeseries):
        """Test that 'today' is accepted in date range"""
        nutrition_timeseries._make_request = Mock()
        nutrition_timeseries.get_time_series_by_date_range(
            resource=NutritionResource.CALORIES_IN, start_date="today", end_date="today"
        )
        nutrition_timeseries._make_request.assert_called_once()

    def test_get_time_series_by_date_range_handles_resources(self, nutrition_timeseries):
        """Test that different nutrition resources are handled correctly"""
        nutrition_timeseries._make_request = Mock()

        # Test CALORIES_IN
        nutrition_timeseries.get_time_series_by_date_range(
            resource=NutritionResource.CALORIES_IN, start_date="2023-01-01", end_date="2023-01-31"
        )
        nutrition_timeseries._make_request.assert_called_with(
            "foods/log/caloriesIn/date/2023-01-01/2023-01-31.json", user_id="-"
        )

        # Test WATER
        nutrition_timeseries._make_request = Mock()
        nutrition_timeseries.get_time_series_by_date_range(
            resource=NutritionResource.WATER, start_date="2023-01-01", end_date="2023-01-31"
        )
        nutrition_timeseries._make_request.assert_called_with(
            "foods/log/water/date/2023-01-01/2023-01-31.json", user_id="-"
        )
