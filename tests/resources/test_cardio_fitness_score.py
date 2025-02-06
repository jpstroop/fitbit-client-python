# tests/resources/test_cardio_fitness_score.py

# Standard library imports
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException
from fitbit_client.resources.cardio_fitness_score import CardioFitnessScoreResource


class TestCardioFitnessResource:
    @fixture
    def cardio_fitness(self, mock_oauth_session, mock_logger):
        """Create a CardioFitnessResource with mocked OAuth session"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return CardioFitnessScoreResource(mock_oauth_session, "en_US", "en_US")

    def test_get_by_date_validates_date_format(self, cardio_fitness):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException) as exc_info:
            cardio_fitness.get_vo2_max_summary_by_date("invalid-date")

        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_by_date_allows_today(self, cardio_fitness):
        """Test that 'today' is accepted as a valid date"""
        cardio_fitness._make_request = Mock()
        cardio_fitness.get_vo2_max_summary_by_date("today")
        cardio_fitness._make_request.assert_called_once()

    def test_get_by_date_allows_valid_date(self, cardio_fitness):
        """Test that valid date format is accepted"""
        cardio_fitness._make_request = Mock()
        cardio_fitness.get_vo2_max_summary_by_date("2023-01-01")
        cardio_fitness._make_request.assert_called_once()

    def test_get_by_interval_validates_date_format(self, cardio_fitness):
        """Test that invalid date format in interval raises InvalidDateException"""
        with raises(InvalidDateException) as exc_info:
            cardio_fitness.get_vo2_max_summary_by_interval("2023-01-01", "invalid-date")

        assert exc_info.value.field_name == "end_date"
        assert "Invalid date format" in str(exc_info.value)

        with raises(InvalidDateException) as exc_info:
            cardio_fitness.get_vo2_max_summary_by_interval("invalid-date", "2023-01-01")

        assert exc_info.value.field_name == "start_date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_by_interval_validates_range_limit(self, cardio_fitness):
        """Test that exceeding 30-day range limit raises InvalidDateRangeException"""
        start_date = "2023-01-01"
        end_date = "2023-02-01"
        with raises(InvalidDateRangeException) as exc_info:
            cardio_fitness.get_vo2_max_summary_by_interval(start_date, end_date)

        assert f"Date range {start_date} to {end_date} exceeds maximum allowed 30 days" in str(
            exc_info.value
        )

    def test_get_by_interval_allows_valid_range(self, cardio_fitness):
        """Test that valid date range is accepted"""
        cardio_fitness._make_request = Mock()
        cardio_fitness.get_vo2_max_summary_by_interval("2023-01-01", "2023-01-15")
        cardio_fitness._make_request.assert_called_once()

    def test_get_by_interval_allows_today(self, cardio_fitness):
        """Test that 'today' is accepted in interval endpoints"""
        cardio_fitness._make_request = Mock()
        cardio_fitness.get_vo2_max_summary_by_interval("today", "today")
        cardio_fitness._make_request.assert_called_once()

    def test_get_by_interval_validates_date_order(self, cardio_fitness):
        """Test that start date must be before or equal to end date"""
        start_date = "2023-01-15"
        end_date = "2023-01-01"
        with raises(InvalidDateRangeException) as exc_info:
            cardio_fitness.get_vo2_max_summary_by_interval(start_date, end_date)

        assert f"Start date {start_date} is after end date {end_date}" in str(exc_info.value)

    def test_get_by_interval_allows_same_date(self, cardio_fitness):
        """Test that same start and end date is allowed"""
        cardio_fitness._make_request = Mock()
        cardio_fitness.get_vo2_max_summary_by_interval("2023-01-01", "2023-01-01")
        cardio_fitness._make_request.assert_called_once()
