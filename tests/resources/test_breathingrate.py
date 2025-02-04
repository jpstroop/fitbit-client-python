# tests/resources/test_breathingrate.py

# Standard library imports
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.breathingrate import BreathingRateResource


class TestBreathingRateResource:
    @fixture
    def breathing_rate(self):
        """Create a BreathingRateResource with mocked OAuth session"""
        mock_oauth = Mock()
        with patch("fitbit_client.resources.base.getLogger"):
            return BreathingRateResource(mock_oauth, "en_US", "en_US")

    def test_get_by_date_validates_date_format(self, breathing_rate):
        """Test that invalid date format raises ValidationException"""
        with raises(ValidationException) as exc_info:
            breathing_rate.get_breathing_rate_summary_by_date("invalid-date")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_by_date_allows_today(self, breathing_rate):
        """Test that 'today' is accepted as a valid date"""
        breathing_rate._make_request = Mock()  # Mock to avoid actual API call
        breathing_rate.get_breathing_rate_summary_by_date("today")
        breathing_rate._make_request.assert_called_once()

    def test_get_by_date_allows_valid_date(self, breathing_rate):
        """Test that valid date format is accepted"""
        breathing_rate._make_request = Mock()  # Mock to avoid actual API call
        breathing_rate.get_breathing_rate_summary_by_date("2023-01-01")
        breathing_rate._make_request.assert_called_once()

    def test_get_by_interval_validates_date_format(self, breathing_rate):
        """Test that invalid date format in interval raises ValidationException"""
        with raises(ValidationException) as exc_info:
            breathing_rate.get_breathing_rate_summary_by_interval("2023-01-01", "invalid-date")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_by_interval_validates_range_limit(self, breathing_rate):
        """Test that exceeding 30-day range limit raises ValidationException"""
        with raises(ValidationException) as exc_info:
            breathing_rate.get_breathing_rate_summary_by_interval("2023-01-01", "2023-02-01")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "date_range"
        assert "Maximum date range is 30 days" in str(exc_info.value)

    def test_get_by_interval_allows_valid_range(self, breathing_rate):
        """Test that valid date range is accepted"""
        breathing_rate._make_request = Mock()  # Mock to avoid actual API call
        breathing_rate.get_breathing_rate_summary_by_interval("2023-01-01", "2023-01-15")
        breathing_rate._make_request.assert_called_once()

    def test_get_by_interval_allows_today(self, breathing_rate):
        """Test that 'today' is accepted in interval endpoints"""
        breathing_rate._make_request = Mock()  # Mock to avoid actual API call
        breathing_rate.get_breathing_rate_summary_by_interval("today", "today")
        breathing_rate._make_request.assert_called_once()
