# tests/resources/test_nutrition_timeseries.py

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException
from fitbit_client.resources.constants import NutritionResource
from fitbit_client.resources.constants import Period
from fitbit_client.resources.nutrition_timeseries import NutritionTimeSeriesResource


class TestNutritionTimeSeriesResource:
    @fixture
    def nutrition_timeseries(self, mock_oauth_session, mock_logger):
        """Create NutritionTimeSeriesResource instance"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return NutritionTimeSeriesResource(mock_oauth_session, "en_US", "en_US")

    def test_get_nutrition_timeseries_by_date_success(
        self, nutrition_timeseries, mock_oauth_session, mock_response_factory
    ):
        """Test successful retrieval of nutrition data by date"""
        expected_response = {"foods-log-caloriesIn": [{"dateTime": "2024-02-13", "value": 2000}]}
        mock_response = mock_response_factory(200, expected_response)
        mock_oauth_session.request.return_value = mock_response

        result = nutrition_timeseries.get_nutrition_timeseries_by_date(
            resource=NutritionResource.CALORIES_IN, date="2024-02-13", period=Period.ONE_DAY
        )

        assert result == expected_response
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/foods/log/caloriesIn/date/2024-02-13/1d.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_nutrition_timeseries_by_date_invalid_date(self, nutrition_timeseries):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException):
            nutrition_timeseries.get_nutrition_timeseries_by_date(
                resource=NutritionResource.CALORIES_IN, date="invalid-date", period=Period.ONE_DAY
            )

    def test_get_nutrition_timeseries_by_date_allows_today(
        self, nutrition_timeseries, mock_oauth_session, mock_response_factory
    ):
        """Test that 'today' is accepted as a valid date"""
        mock_response = mock_response_factory(200, {"foods-log-caloriesIn": []})
        mock_oauth_session.request.return_value = mock_response

        # Should not raise an exception
        nutrition_timeseries.get_nutrition_timeseries_by_date(
            resource=NutritionResource.CALORIES_IN, date="today", period=Period.ONE_DAY
        )

    def test_get_nutrition_timeseries_by_date_range_success(
        self, nutrition_timeseries, mock_oauth_session, mock_response_factory
    ):
        """Test successful retrieval of nutrition data by date range"""
        expected_response = {
            "foods-log-caloriesIn": [
                {"dateTime": "2024-02-13", "value": 2000},
                {"dateTime": "2024-02-14", "value": 2100},
            ]
        }
        mock_response = mock_response_factory(200, expected_response)
        mock_oauth_session.request.return_value = mock_response

        result = nutrition_timeseries.get_nutrition_timeseries_by_date_range(
            resource=NutritionResource.CALORIES_IN, start_date="2024-02-13", end_date="2024-02-14"
        )

        assert result == expected_response
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/foods/log/caloriesIn/date/2024-02-13/2024-02-14.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_nutrition_timeseries_by_date_range_invalid_dates(self, nutrition_timeseries):
        """Test that invalid date formats raise InvalidDateException"""
        with raises(InvalidDateException):
            nutrition_timeseries.get_nutrition_timeseries_by_date_range(
                resource=NutritionResource.CALORIES_IN, start_date="invalid", end_date="2024-02-14"
            )

        with raises(InvalidDateException):
            nutrition_timeseries.get_nutrition_timeseries_by_date_range(
                resource=NutritionResource.CALORIES_IN, start_date="2024-02-13", end_date="invalid"
            )

    def test_get_nutrition_timeseries_by_date_range_invalid_range(self, nutrition_timeseries):
        """Test that end date before start date raises InvalidDateRangeException"""
        with raises(InvalidDateRangeException):
            nutrition_timeseries.get_nutrition_timeseries_by_date_range(
                resource=NutritionResource.CALORIES_IN,
                start_date="2024-02-14",
                end_date="2024-02-13",
            )

    def test_get_nutrition_timeseries_by_date_range_exceeds_max_days(self, nutrition_timeseries):
        """Test that exceeding 1095 days raises InvalidDateRangeException"""
        with raises(InvalidDateRangeException) as exc_info:
            nutrition_timeseries.get_nutrition_timeseries_by_date_range(
                resource=NutritionResource.CALORIES_IN,
                start_date="2020-01-01",
                end_date="2024-01-01",
            )  # More than 1095 days
        assert "Date range 2020-01-01 to 2024-01-01 exceeds maximum allowed 1095 days" in str(
            exc_info.value
        )

    def test_get_nutrition_timeseries_by_date_range_allows_today(
        self, nutrition_timeseries, mock_oauth_session, mock_response_factory
    ):
        """Test that 'today' is accepted in date range"""
        mock_response = mock_response_factory(200, {"foods-log-caloriesIn": []})
        mock_oauth_session.request.return_value = mock_response

        # Should not raise an exception
        nutrition_timeseries.get_nutrition_timeseries_by_date_range(
            resource=NutritionResource.CALORIES_IN, start_date="today", end_date="today"
        )
