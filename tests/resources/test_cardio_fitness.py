# tests/resources/test_cardio_fitness.py

# Standard library imports
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.cardio_fitness import CardioFitnessResource


class TestCardioFitnessResource:
    @fixture
    def cardio_fitness(self):
        """Create a CardioFitnessResource with mocked OAuth session"""
        mock_oauth = Mock()
        with patch("fitbit_client.resources.base.getLogger"):
            return CardioFitnessResource(mock_oauth, "en_US", "en_US")

    def test_get_by_date_validates_date_format(self, cardio_fitness):
        """Test that invalid date format raises ValidationException"""
        with raises(ValidationException) as exc_info:
            cardio_fitness.get_vo2_max_summary_by_date("invalid-date")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_by_date_allows_today(self, cardio_fitness):
        """Test that 'today' is accepted as a valid date"""
        cardio_fitness._make_request = Mock()  # Mock to avoid actual API call
        cardio_fitness.get_vo2_max_summary_by_date("today")
        cardio_fitness._make_request.assert_called_once()

    def test_get_by_date_allows_valid_date(self, cardio_fitness):
        """Test that valid date format is accepted"""
        cardio_fitness._make_request = Mock()  # Mock to avoid actual API call
        cardio_fitness.get_vo2_max_summary_by_date("2023-01-01")
        cardio_fitness._make_request.assert_called_once()

    def test_get_by_interval_validates_date_format(self, cardio_fitness):
        """Test that invalid date format in interval raises ValidationException"""
        with raises(ValidationException) as exc_info:
            cardio_fitness.get_vo2_max_summary_by_interval("2023-01-01", "invalid-date")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_by_interval_validates_range_limit(self, cardio_fitness):
        """Test that exceeding 30-day range limit raises ValidationException"""
        with raises(ValidationException) as exc_info:
            cardio_fitness.get_vo2_max_summary_by_interval("2023-01-01", "2023-02-01")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "date_range"
        assert "Maximum date range is 30 days" in str(exc_info.value)

    def test_get_by_interval_allows_valid_range(self, cardio_fitness):
        """Test that valid date range is accepted"""
        cardio_fitness._make_request = Mock()  # Mock to avoid actual API call
        cardio_fitness.get_vo2_max_summary_by_interval("2023-01-01", "2023-01-15")
        cardio_fitness._make_request.assert_called_once()

    def test_get_by_interval_allows_today(self, cardio_fitness):
        """Test that 'today' is accepted in interval endpoints"""
        cardio_fitness._make_request = Mock()  # Mock to avoid actual API call
        cardio_fitness.get_vo2_max_summary_by_interval("today", "today")
        cardio_fitness._make_request.assert_called_once()
