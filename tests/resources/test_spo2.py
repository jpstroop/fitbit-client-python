# tests/resources/test_spo2.py

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException
from fitbit_client.resources.spo2 import SpO2Resource


class TestSpO2Resource:
    @fixture
    def spo2_resource(self, mock_oauth_session, mock_logger):
        """Create SpO2Resource instance with mocked dependencies"""
        mock_oauth_session.token = {"expires_at": 1234567890}
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return SpO2Resource(mock_oauth_session, "en_US", "en_US")

    def test_get_spo2_summary_by_date_success(
        self, spo2_resource, mock_oauth_session, mock_response_factory
    ):
        """Test successful retrieval of SpO2 summary by date"""
        expected_response = {"dateTime": "2024-02-13", "value": {"avg": 96, "min": 94, "max": 98}}
        mock_response = mock_response_factory(200, expected_response)
        mock_oauth_session.request.return_value = mock_response

        result = spo2_resource.get_spo2_summary_by_date("2024-02-13")

        assert result == expected_response
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/spo2/date/2024-02-13.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_spo2_summary_by_date_invalid_date(self, spo2_resource, mock_oauth_session):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException):
            spo2_resource.get_spo2_summary_by_date("invalid-date")

    def test_get_spo2_summary_by_date_allows_today(
        self, spo2_resource, mock_oauth_session, mock_response_factory
    ):
        """Test that 'today' is accepted as a valid date"""
        mock_response = mock_response_factory(200, {"dateTime": "today"})
        mock_oauth_session.request.return_value = mock_response

        # Should not raise an exception
        spo2_resource.get_spo2_summary_by_date("today")

    def test_get_spo2_summary_by_interval_success(
        self, spo2_resource, mock_oauth_session, mock_response_factory
    ):
        """Test successful retrieval of SpO2 summary by date range"""
        expected_response = {
            "spo2": [
                {"dateTime": "2024-02-13", "value": {"avg": 96, "min": 94, "max": 98}},
                {"dateTime": "2024-02-14", "value": {"avg": 97, "min": 95, "max": 99}},
            ]
        }
        mock_response = mock_response_factory(200, expected_response)
        mock_oauth_session.request.return_value = mock_response

        result = spo2_resource.get_spo2_summary_by_interval(
            start_date="2024-02-13", end_date="2024-02-14"
        )

        assert result == expected_response
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/spo2/date/2024-02-13/2024-02-14.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_spo2_summary_by_interval_invalid_dates(self, spo2_resource, mock_oauth_session):
        """Test that invalid date formats raise InvalidDateException"""
        with raises(InvalidDateException):
            spo2_resource.get_spo2_summary_by_interval(start_date="invalid", end_date="2024-02-14")

        with raises(InvalidDateException):
            spo2_resource.get_spo2_summary_by_interval(start_date="2024-02-13", end_date="invalid")

    def test_get_spo2_summary_by_interval_invalid_range(self, spo2_resource, mock_oauth_session):
        """Test that end date before start date raises InvalidDateRangeException"""
        with raises(InvalidDateRangeException):
            spo2_resource.get_spo2_summary_by_interval(
                start_date="2024-02-14", end_date="2024-02-13"
            )

    def test_get_spo2_summary_by_interval_allows_today(
        self, spo2_resource, mock_oauth_session, mock_response_factory
    ):
        """Test that 'today' is accepted in date range"""
        mock_response = mock_response_factory(200, {"spo2": []})
        mock_oauth_session.request.return_value = mock_response

        # Should not raise an exception
        spo2_resource.get_spo2_summary_by_interval("today", "today")
