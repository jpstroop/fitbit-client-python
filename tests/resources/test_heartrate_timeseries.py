# tests/resources/test_heartrate_timeseries.py

# Standard library imports
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises
from requests import Response

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException
from fitbit_client.resources.constants import Period
from fitbit_client.resources.heartrate_timeseries import HeartrateTimeSeriesResource


class TestHeartRateTimeSeriesResource:
    """Tests for the Heart Rate Time Series resource"""

    @fixture
    def heartrate_resource(self, mock_oauth_session, mock_logger):
        """Fixture to provide a HeartrateTimeSeriesResource instance"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return HeartrateTimeSeriesResource(
                oauth_session=mock_oauth_session, locale="en_US", language="en_US"
            )

    def test_get_heartrate_timeseries_by_date_success(
        self, heartrate_resource, mock_oauth_session, mock_response
    ):
        """Test successful retrieval of heart rate data by date and period"""
        # Setup response
        response_data = {
            "activities-heart": [
                {
                    "dateTime": "2024-02-10",
                    "value": {
                        "customHeartRateZones": [],
                        "heartRateZones": [
                            {
                                "name": "Out of Range",
                                "minutes": 180,
                                "caloriesOut": 500,
                                "min": 30,
                                "max": 90,
                            }
                        ],
                        "restingHeartRate": 65,
                    },
                }
            ]
        }

        mock_response.json.return_value = response_data
        mock_oauth_session.request.return_value = mock_response

        result = heartrate_resource.get_heartrate_timeseries_by_date(
            date="2024-02-10", period=Period.ONE_DAY
        )

        assert result == response_data
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/activities/heart/date/2024-02-10/1d.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_heartrate_timeseries_by_date_invalid_date(self, heartrate_resource):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException):
            heartrate_resource.get_heartrate_timeseries_by_date(
                date="invalid-date", period=Period.ONE_DAY
            )

    def test_get_heartrate_timeseries_by_date_today(self, heartrate_resource, mock_response):
        """Test that 'today' is accepted as a valid date"""
        mock_response.json.return_value = {"activities-heart": []}
        heartrate_resource.oauth.request.return_value = mock_response

        result = heartrate_resource.get_heartrate_timeseries_by_date(
            date="today", period=Period.ONE_DAY
        )

        assert result == {"activities-heart": []}
        heartrate_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/activities/heart/date/today/1d.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_heartrate_timeseries_by_date_invalid_period(self, heartrate_resource):
        """Test that error is raised for unsupported period"""
        with raises(ValueError) as exc_info:
            heartrate_resource.get_heartrate_timeseries_by_date(
                date="2024-02-10", period=Period.ONE_YEAR
            )

        error_msg = str(exc_info.value)
        assert error_msg.startswith("Period must be one of: ")
        assert all(period in error_msg for period in ["1d", "7d", "30d", "1w", "1m"])

    def test_get_heartrate_timeseries_by_date_invalid_timezone(self, heartrate_resource):
        """Test that error is raised for unsupported timezone"""
        with raises(ValueError) as exc_info:
            heartrate_resource.get_heartrate_timeseries_by_date(
                date="2024-02-10", period=Period.ONE_DAY, timezone="EST"
            )

        assert str(exc_info.value) == "Only 'UTC' timezone is supported"

    def test_get_heartrate_timeseries_by_date_range_success(
        self, heartrate_resource, mock_response
    ):
        """Test successful retrieval of heart rate data by date range"""
        response_data = {
            "activities-heart": [
                {"dateTime": "2024-02-10", "value": {"restingHeartRate": 65, "heartRateZones": []}},
                {"dateTime": "2024-02-11", "value": {"restingHeartRate": 68, "heartRateZones": []}},
            ]
        }

        mock_response.json.return_value = response_data
        heartrate_resource.oauth.request.return_value = mock_response

        result = heartrate_resource.get_heartrate_timeseries_by_date_range(
            start_date="2024-02-10", end_date="2024-02-11"
        )

        assert result == response_data
        heartrate_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/activities/heart/date/2024-02-10/2024-02-11.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_heartrate_timeseries_by_date_range_invalid_dates(self, heartrate_resource):
        """Test that invalid date formats raise InvalidDateException"""
        with raises(InvalidDateException):
            heartrate_resource.get_heartrate_timeseries_by_date_range(
                start_date="invalid", end_date="2024-02-11"
            )

        with raises(InvalidDateException):
            heartrate_resource.get_heartrate_timeseries_by_date_range(
                start_date="2024-02-10", end_date="invalid"
            )

    def test_get_heartrate_timeseries_by_date_range_invalid_range(self, heartrate_resource):
        """Test that end date before start date raises InvalidDateRangeException"""
        with raises(InvalidDateRangeException):
            heartrate_resource.get_heartrate_timeseries_by_date_range(
                start_date="2024-02-11", end_date="2024-02-10"
            )

    def test_get_heartrate_timeseries_by_date_range_invalid_timezone(self, heartrate_resource):
        """Test that invalid timezone raises ValueError"""
        with raises(ValueError) as exc_info:
            heartrate_resource.get_heartrate_timeseries_by_date_range(
                start_date="2024-02-10", end_date="2024-02-11", timezone="EST"
            )

        assert str(exc_info.value) == "Only 'UTC' timezone is supported"

    def test_get_heartrate_timeseries_by_date_range_today(self, heartrate_resource, mock_response):
        """Test that 'today' is accepted in date range"""
        mock_response.json.return_value = {"activities-heart": []}
        heartrate_resource.oauth.request.return_value = mock_response

        result = heartrate_resource.get_heartrate_timeseries_by_date_range(
            start_date="today", end_date="today"
        )

        assert result == {"activities-heart": []}
        heartrate_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/activities/heart/date/today/today.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )
