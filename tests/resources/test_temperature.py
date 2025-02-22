# tests/resources/test_temperature.py

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException
from fitbit_client.resources.temperature import TemperatureResource


class TestTemperatureResource:
    @fixture
    def temperature_resource(self, mock_oauth_session, mock_logger):
        """Create TemperatureResource instance with mocked dependencies"""
        mock_oauth_session.token = {"expires_at": 1234567890}
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return TemperatureResource(mock_oauth_session, "en_US", "en_US")

    def test_get_temperature_core_summary_by_date_success(
        self, temperature_resource, mock_oauth_session, mock_response_factory
    ):
        """Test successful retrieval of core temperature summary by date"""
        expected_response = {
            "dateTime": "2024-02-13",
            "value": {"datetime": "2024-02-13T12:00:00", "temp": 37.2},
        }
        mock_response = mock_response_factory(200, expected_response)
        mock_oauth_session.request.return_value = mock_response

        result = temperature_resource.get_temperature_core_summary_by_date("2024-02-13")

        assert result == expected_response
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/temp/core/date/2024-02-13.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_temperature_core_summary_by_date_invalid_date(
        self, temperature_resource, mock_oauth_session
    ):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException):
            temperature_resource.get_temperature_core_summary_by_date("invalid-date")

    def test_get_temperature_core_summary_by_date_allows_today(
        self, temperature_resource, mock_oauth_session, mock_response_factory
    ):
        """Test that 'today' is accepted as a valid date"""
        mock_response = mock_response_factory(200, {"dateTime": "today"})
        mock_oauth_session.request.return_value = mock_response

        # Should not raise an exception
        temperature_resource.get_temperature_core_summary_by_date("today")

    def test_get_temperature_core_summary_by_interval_success(
        self, temperature_resource, mock_oauth_session, mock_response_factory
    ):
        """Test successful retrieval of core temperature summary by date range"""
        expected_response = {
            "temp-core": [
                {
                    "dateTime": "2024-02-13",
                    "value": {"datetime": "2024-02-13T12:00:00", "temp": 37.2},
                },
                {
                    "dateTime": "2024-02-14",
                    "value": {"datetime": "2024-02-14T12:00:00", "temp": 37.1},
                },
            ]
        }
        mock_response = mock_response_factory(200, expected_response)
        mock_oauth_session.request.return_value = mock_response

        result = temperature_resource.get_temperature_core_summary_by_interval(
            start_date="2024-02-13", end_date="2024-02-14"
        )

        assert result == expected_response
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/temp/core/date/2024-02-13/2024-02-14.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_temperature_core_summary_by_interval_invalid_dates(
        self, temperature_resource, mock_oauth_session
    ):
        """Test that invalid date formats raise InvalidDateException"""
        with raises(InvalidDateException):
            temperature_resource.get_temperature_core_summary_by_interval(
                start_date="invalid", end_date="2024-02-14"
            )

        with raises(InvalidDateException):
            temperature_resource.get_temperature_core_summary_by_interval(
                start_date="2024-02-13", end_date="invalid"
            )

    def test_get_temperature_core_summary_by_interval_invalid_range(
        self, temperature_resource, mock_oauth_session
    ):
        """Test that end date before start date raises InvalidDateRangeException"""
        with raises(InvalidDateRangeException):
            temperature_resource.get_temperature_core_summary_by_interval(
                start_date="2024-02-14", end_date="2024-02-13"
            )

    def test_get_temperature_core_summary_by_interval_exceeds_max_days(
        self, temperature_resource, mock_oauth_session
    ):
        """Test that exceeding 30 days raises InvalidDateRangeException"""
        with raises(InvalidDateRangeException) as exc_info:
            temperature_resource.get_temperature_core_summary_by_interval(
                start_date="2024-02-13", end_date="2024-03-15"
            )  # More than 30 days
        assert "Date range 2024-02-13 to 2024-03-15 exceeds maximum allowed 30 days" in str(
            exc_info.value
        )

    def test_get_temperature_core_summary_by_interval_allows_today(
        self, temperature_resource, mock_oauth_session, mock_response_factory
    ):
        """Test that 'today' is accepted in date range"""
        mock_response = mock_response_factory(200, {"temp-core": []})
        mock_oauth_session.request.return_value = mock_response

        # Should not raise an exception
        temperature_resource.get_temperature_core_summary_by_interval("today", "today")

    def test_get_temperature_skin_summary_by_date_success(
        self, temperature_resource, mock_oauth_session, mock_response_factory
    ):
        """Test successful retrieval of skin temperature summary by date"""
        expected_response = {
            "dateTime": "2024-02-13",
            "value": {"temp": {"deviation": 0.2, "baseline": 32.5}},
        }
        mock_response = mock_response_factory(200, expected_response)
        mock_oauth_session.request.return_value = mock_response

        result = temperature_resource.get_temperature_skin_summary_by_date("2024-02-13")

        assert result == expected_response
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/temp/skin/date/2024-02-13.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_temperature_skin_summary_by_date_invalid_date(
        self, temperature_resource, mock_oauth_session
    ):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException):
            temperature_resource.get_temperature_skin_summary_by_date("invalid-date")

    def test_get_temperature_skin_summary_by_date_allows_today(
        self, temperature_resource, mock_oauth_session, mock_response_factory
    ):
        """Test that 'today' is accepted as a valid date"""
        mock_response = mock_response_factory(200, {"dateTime": "today"})
        mock_oauth_session.request.return_value = mock_response

        # Should not raise an exception
        temperature_resource.get_temperature_skin_summary_by_date("today")

    def test_get_temperature_skin_summary_by_interval_success(
        self, temperature_resource, mock_oauth_session, mock_response_factory
    ):
        """Test successful retrieval of skin temperature summary by date range"""
        expected_response = {
            "temp-skin": [
                {"dateTime": "2024-02-13", "value": {"temp": {"deviation": 0.2, "baseline": 32.5}}},
                {"dateTime": "2024-02-14", "value": {"temp": {"deviation": 0.1, "baseline": 32.5}}},
            ]
        }
        mock_response = mock_response_factory(200, expected_response)
        mock_oauth_session.request.return_value = mock_response

        result = temperature_resource.get_temperature_skin_summary_by_interval(
            start_date="2024-02-13", end_date="2024-02-14"
        )

        assert result == expected_response
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/temp/skin/date/2024-02-13/2024-02-14.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_temperature_skin_summary_by_interval_invalid_dates(
        self, temperature_resource, mock_oauth_session
    ):
        """Test that invalid date formats raise InvalidDateException"""
        with raises(InvalidDateException):
            temperature_resource.get_temperature_skin_summary_by_interval(
                start_date="invalid", end_date="2024-02-14"
            )

        with raises(InvalidDateException):
            temperature_resource.get_temperature_skin_summary_by_interval(
                start_date="2024-02-13", end_date="invalid"
            )

    def test_get_temperature_skin_summary_by_interval_invalid_range(
        self, temperature_resource, mock_oauth_session
    ):
        """Test that end date before start date raises InvalidDateRangeException"""
        with raises(InvalidDateRangeException):
            temperature_resource.get_temperature_skin_summary_by_interval(
                start_date="2024-02-14", end_date="2024-02-13"
            )

    def test_get_temperature_skin_summary_by_interval_exceeds_max_days(
        self, temperature_resource, mock_oauth_session
    ):
        """Test that exceeding 30 days raises InvalidDateRangeException"""
        with raises(InvalidDateRangeException) as exc_info:
            temperature_resource.get_temperature_skin_summary_by_interval(
                start_date="2024-02-13", end_date="2024-03-15"
            )  # More than 30 days
        assert "Date range 2024-02-13 to 2024-03-15 exceeds maximum allowed 30 days" in str(
            exc_info.value
        )

    def test_get_temperature_skin_summary_by_interval_allows_today(
        self, temperature_resource, mock_oauth_session, mock_response_factory
    ):
        """Test that 'today' is accepted in date range"""
        mock_response = mock_response_factory(200, {"temp-skin": []})
        mock_oauth_session.request.return_value = mock_response

        # Should not raise an exception
        temperature_resource.get_temperature_skin_summary_by_interval("today", "today")
