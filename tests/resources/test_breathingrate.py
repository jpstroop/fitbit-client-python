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
        # Test invalid end date
        with raises(ValidationException) as exc_info:
            breathing_rate.get_breathing_rate_summary_by_interval("2023-01-01", "invalid-date")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "end_date"
        assert "Invalid date format" in str(exc_info.value)

        # Test invalid start date
        with raises(ValidationException) as exc_info:
            breathing_rate.get_breathing_rate_summary_by_interval("invalid-date", "2023-01-01")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "start_date"
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

    def test_get_by_interval_validates_date_order(self, breathing_rate):
        """Test that start date must be before or equal to end date"""
        with raises(ValidationException) as exc_info:
            breathing_rate.get_breathing_rate_summary_by_interval("2023-01-15", "2023-01-01")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "date_range"
        assert "Start date must be before or equal to end date" in str(exc_info.value)

    def test_get_by_interval_allows_same_date(self, breathing_rate):
        """Test that same start and end date is allowed"""
        breathing_rate._make_request = Mock()
        breathing_rate.get_breathing_rate_summary_by_interval("2023-01-01", "2023-01-01")
        breathing_rate._make_request.assert_called_once()

    def test_successful_response_format(self, breathing_rate, mock_response_factory):
        """Test successful response matches expected format from API docs"""
        mock_response = mock_response_factory(
            200, {"br": [{"value": {"breathingRate": 17.8}, "dateTime": "2023-01-01"}]}
        )
        breathing_rate.oauth.request.return_value = mock_response

        result = breathing_rate.get_breathing_rate_summary_by_date("2023-01-01")

        assert "br" in result
        assert isinstance(result["br"], list)
        assert "value" in result["br"][0]
        assert "breathingRate" in result["br"][0]["value"]
        assert "dateTime" in result["br"][0]

    def test_intraday_by_date_not_implemented(self, breathing_rate):
        """Test that intraday by date endpoint raises NotImplementedError"""
        with raises(NotImplementedError):
            breathing_rate.get_breathing_rate_intraday_by_date("2023-01-01")

    def test_intraday_by_interval_not_implemented(self, breathing_rate):
        """Test that intraday by interval endpoint raises NotImplementedError"""
        with raises(NotImplementedError):
            breathing_rate.get_breathing_rate_intraday_by_interval("2023-01-01", "2023-01-02")
