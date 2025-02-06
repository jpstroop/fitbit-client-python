# tests/resources/test_heartrate_variability.py

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException
from fitbit_client.resources.heartrate_variability import HeartrateVariabilityResource


class TestHeartrateVariabilityResource:
    @fixture
    def hrv_resource(self, mock_oauth_session, mock_logger):
        """Create HeartrateVariabilityResource instance with mocked dependencies"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return HeartrateVariabilityResource(mock_oauth_session, "en_US", "en_US")

    def test_get_hrv_summary_by_date_success(
        self, hrv_resource, mock_oauth_session, mock_response_factory
    ):
        """Test successful retrieval of HRV data for a single date"""
        expected_response = {
            "hrv": [
                {"dateTime": "2024-02-13", "value": {"dailyRmssd": 34.938, "deepRmssd": 31.567}}
            ]
        }
        mock_response = mock_response_factory(200, expected_response)
        mock_oauth_session.request.return_value = mock_response

        result = hrv_resource.get_hrv_summary_by_date("2024-02-13")

        assert result == expected_response
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/hrv/date/2024-02-13.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_hrv_summary_by_date_today(
        self, hrv_resource, mock_oauth_session, mock_response_factory
    ):
        """Test HRV data retrieval using 'today' as date parameter"""
        mock_response = mock_response_factory(200, {"hrv": []})
        mock_oauth_session.request.return_value = mock_response

        # Should not raise an exception
        hrv_resource.get_hrv_summary_by_date("today")

    def test_get_hrv_summary_by_date_invalid_date(self, hrv_resource):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException):
            hrv_resource.get_hrv_summary_by_date("invalid-date")

    def test_get_hrv_summary_by_interval_success(
        self, hrv_resource, mock_oauth_session, mock_response_factory
    ):
        """Test successful retrieval of HRV data for a date range"""
        expected_response = {
            "hrv": [
                {"dateTime": "2024-02-13", "value": {"dailyRmssd": 62.887, "deepRmssd": 64.887}},
                {"dateTime": "2024-02-14", "value": {"dailyRmssd": 61.887, "deepRmssd": 64.887}},
            ]
        }
        mock_response = mock_response_factory(200, expected_response)
        mock_oauth_session.request.return_value = mock_response

        result = hrv_resource.get_hrv_summary_by_interval("2024-02-13", "2024-02-14")

        assert result == expected_response
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/hrv/date/2024-02-13/2024-02-14.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_hrv_summary_by_interval_invalid_dates(self, hrv_resource):
        """Test that invalid date formats raise InvalidDateException"""
        with raises(InvalidDateException):
            hrv_resource.get_hrv_summary_by_interval("invalid", "2024-02-14")

        with raises(InvalidDateException):
            hrv_resource.get_hrv_summary_by_interval("2024-02-13", "invalid")

    def test_get_hrv_summary_by_interval_invalid_range(self, hrv_resource):
        """Test that end date before start date raises InvalidDateRangeException"""
        with raises(InvalidDateRangeException):
            hrv_resource.get_hrv_summary_by_interval("2024-02-14", "2024-02-13")

    def test_get_hrv_summary_by_interval_today(
        self, hrv_resource, mock_oauth_session, mock_response_factory
    ):
        """Test that 'today' is accepted in date range"""
        mock_response = mock_response_factory(200, {"hrv": []})
        mock_oauth_session.request.return_value = mock_response

        # Should not raise an exception
        hrv_resource.get_hrv_summary_by_interval("today", "today")
