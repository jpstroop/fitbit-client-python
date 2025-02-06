# tests/resources/test_breathingrate.py

# Standard library imports
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException
from fitbit_client.resources.breathingrate import BreathingRateResource


class TestBreathingRateResource:

    @fixture()
    def breathing_rate_resource(mock_oauth_session, mock_logger):
        """Create a BreathingRateResource with mocked OAuth session"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return BreathingRateResource(mock_oauth_session, "en_US", "en_US")

    def test_get_by_date_validates_date_format(self, breathing_rate_resource):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException) as exc_info:
            breathing_rate_resource.get_breathing_rate_summary_by_date("invalid-date")

        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_by_date_allows_today(self, breathing_rate_resource):
        """Test that 'today' is accepted as a valid date"""
        breathing_rate_resource._make_request = Mock()  # Mock to avoid actual API call
        breathing_rate_resource.get_breathing_rate_summary_by_date("today")
        breathing_rate_resource._make_request.assert_called_once()

    def test_get_by_interval_validates_date_range(self, breathing_rate_resource):
        """Test that exceeding 30-day range limit raises InvalidDateRangeException"""
        start_date = "2023-01-01"
        end_date = "2023-02-01"
        with raises(InvalidDateRangeException) as exc_info:
            breathing_rate_resource.get_breathing_rate_summary_by_interval(start_date, end_date)
        assert f"Date range {start_date} to {end_date} exceeds maximum allowed 30 days" in str(
            exc_info.value
        )

    def test_get_by_interval_validates_date_order(self, breathing_rate_resource):
        """Test that start date must be before or equal to end date"""
        start_date = "2023-01-15"
        end_date = "2023-01-01"
        with raises(InvalidDateRangeException) as exc_info:
            breathing_rate_resource.get_breathing_rate_summary_by_interval(start_date, end_date)

        assert f"Start date {start_date} is after end date {end_date}" in str(exc_info.value)

    def test_get_by_interval_allows_same_date(self, breathing_rate_resource):
        """Test that same start and end date is allowed"""
        breathing_rate_resource._make_request = Mock()
        breathing_rate_resource.get_breathing_rate_summary_by_interval("2023-01-01", "2023-01-01")
        breathing_rate_resource._make_request.assert_called_once()
