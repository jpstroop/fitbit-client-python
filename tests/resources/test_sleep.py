# tests/resources/test_sleep.py

# Standard library imports
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.constants import SleepType
from fitbit_client.resources.sleep import SleepResource


class TestSleepResource:

    @fixture
    def sleep_resource(self, mock_oauth_session, mock_logger):
        """Fixture to provide a SleepResource instance"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return SleepResource(oauth_session=mock_oauth_session, locale="en_US", language="en_US")

    # [... all existing tests remain exactly the same ...]

    def test_get_sleep_log_by_date_validates_date_format(self, sleep_resource):
        """Test that invalid date format raises ValidationException"""
        with raises(ValidationException) as exc_info:
            sleep_resource.get_sleep_log_by_date("invalid-date")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_sleep_log_by_date_allows_today(
        self, sleep_resource, mock_oauth_session, mock_response
    ):
        """Test that 'today' is accepted as a valid date"""
        mock_response.json.return_value = {"sleep": []}
        mock_response.headers = {"content-type": "application/json"}
        mock_oauth_session.request.return_value = mock_response

        sleep_resource.get_sleep_log_by_date("today")
        mock_oauth_session.request.assert_called_once()

    def test_get_sleep_log_by_date_range_validates_start_date(self, sleep_resource):
        """Test that invalid start date format raises ValidationException"""
        with raises(ValidationException) as exc_info:
            sleep_resource.get_sleep_log_by_date_range("invalid-date", "2023-01-01")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_sleep_log_by_date_range_validates_end_date(self, sleep_resource):
        """Test that invalid end date format raises ValidationException"""
        with raises(ValidationException) as exc_info:
            sleep_resource.get_sleep_log_by_date_range("2023-01-01", "invalid-date")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_sleep_log_by_date_range_validates_max_range(self, sleep_resource):
        """Test that exceeding 100-day range limit raises ValidationException"""
        with raises(ValidationException) as exc_info:
            sleep_resource.get_sleep_log_by_date_range("2023-01-01", "2023-05-01")  # ~120 days

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "date_range"
        assert "Maximum date range is 100 days" in str(exc_info.value)

    def test_get_sleep_log_by_date_range_allows_valid_range(
        self, sleep_resource, mock_oauth_session, mock_response
    ):
        """Test that valid date range is accepted"""
        mock_response.json.return_value = {"sleep": []}
        mock_response.headers = {"content-type": "application/json"}
        mock_oauth_session.request.return_value = mock_response

        # Test range just under limit (99 days)
        sleep_resource.get_sleep_log_by_date_range("2023-01-01", "2023-04-10")
        mock_oauth_session.request.assert_called_once()

    def test_get_sleep_log_by_date_range_allows_today(
        self, sleep_resource, mock_oauth_session, mock_response
    ):
        """Test that 'today' is accepted in date range"""
        mock_response.json.return_value = {"sleep": []}
        mock_response.headers = {"content-type": "application/json"}
        mock_oauth_session.request.return_value = mock_response

        sleep_resource.get_sleep_log_by_date_range("today", "today")
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1.2/user/-/sleep/date/today/today.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )
