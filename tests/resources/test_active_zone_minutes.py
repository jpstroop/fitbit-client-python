# tests/resources/test_active_zone_minutes.py

# Standard library imports
from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException
from fitbit_client.resources.active_zone_minutes import ActiveZoneMinutesResource
from fitbit_client.resources.constants import Period


class TestActiveZoneMinutesResource:
    """Tests for the Active Zone Minutes resource"""

    @fixture
    def azm_resource(self, mock_oauth_session, mock_logger):
        """Fixture to provide an ActiveZoneMinutesResource instance"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return ActiveZoneMinutesResource(
                oauth_session=mock_oauth_session, locale="en_US", language="en_US"
            )

    def test_get_azm_timeseries_by_date_success(self, azm_resource, mock_response):
        """Test successful retrieval of AZM time series by date with default period"""
        # Setup response
        mock_response.json.return_value = {
            "activities-active-zone-minutes": [
                {
                    "dateTime": "2025-02-01",
                    "value": {
                        "activeZoneMinutes": 102,
                        "fatBurnActiveZoneMinutes": 90,
                        "cardioActiveZoneMinutes": 8,
                        "peakActiveZoneMinutes": 4,
                    },
                }
            ]
        }
        azm_resource.oauth.request.return_value = mock_response

        # Execute request
        result = azm_resource.get_azm_timeseries_by_date(date="2025-02-01")

        # Verify results
        assert result == mock_response.json.return_value
        azm_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/2025-02-01/1d.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_azm_timeseries_by_date_explicit_period(self, azm_resource, mock_response):
        """Test successful retrieval of AZM time series by date with explicit ONE_DAY period"""
        mock_response.json.return_value = {"activities-active-zone-minutes": []}
        azm_resource.oauth.request.return_value = mock_response

        result = azm_resource.get_azm_timeseries_by_date(date="2025-02-01", period=Period.ONE_DAY)

        assert result == mock_response.json.return_value
        azm_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/2025-02-01/1d.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_azm_timeseries_by_date_invalid_period(self, azm_resource):
        """Test that using any period other than ONE_DAY raises ValueError"""
        invalid_periods = [
            Period.SEVEN_DAYS,
            Period.THIRTY_DAYS,
            Period.ONE_WEEK,
            Period.ONE_MONTH,
            Period.THREE_MONTHS,
            Period.SIX_MONTHS,
            Period.ONE_YEAR,
            Period.MAX,
        ]

        for period in invalid_periods:
            with raises(ValueError) as exc_info:
                azm_resource.get_azm_timeseries_by_date(date="2025-02-01", period=period)
            assert "Only 1d period is supported for AZM time series" in str(exc_info.value)

    def test_get_azm_timeseries_by_date_invalid_date(self, azm_resource):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException) as exc_info:
            azm_resource.get_azm_timeseries_by_date(date="invalid-date")
        assert "invalid-date" in str(exc_info.value)
        assert exc_info.value.field_name == "date"

    def test_get_azm_timeseries_by_date_with_user_id(self, azm_resource, mock_response):
        """Test getting AZM time series for a specific user"""
        mock_response.json.return_value = {"activities-active-zone-minutes": []}
        azm_resource.oauth.request.return_value = mock_response

        result = azm_resource.get_azm_timeseries_by_date(date="2025-02-01", user_id="123ABC")

        assert result == mock_response.json.return_value
        azm_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/123ABC/activities/active-zone-minutes/date/2025-02-01/1d.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_azm_timeseries_by_interval_success(self, azm_resource, mock_response):
        """Test successful retrieval of AZM time series by date range"""
        mock_response.json.return_value = {
            "activities-active-zone-minutes": [
                {
                    "dateTime": "2025-02-01",
                    "value": {
                        "activeZoneMinutes": 102,
                        "fatBurnActiveZoneMinutes": 90,
                        "cardioActiveZoneMinutes": 8,
                        "peakActiveZoneMinutes": 4,
                    },
                },
                {
                    "dateTime": "2025-02-02",
                    "value": {
                        "activeZoneMinutes": 47,
                        "fatBurnActiveZoneMinutes": 43,
                        "cardioActiveZoneMinutes": 4,
                    },
                },
            ]
        }
        azm_resource.oauth.request.return_value = mock_response

        result = azm_resource.get_azm_timeseries_by_interval(
            start_date="2025-02-01", end_date="2025-02-02"
        )

        assert result == mock_response.json.return_value
        azm_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/2025-02-01/2025-02-02.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_azm_timeseries_by_interval_invalid_dates(self, azm_resource):
        """Test that invalid date formats raise InvalidDateException"""
        with raises(InvalidDateException) as exc_info:
            azm_resource.get_azm_timeseries_by_interval(start_date="invalid", end_date="2024-02-01")
        assert "invalid" in str(exc_info.value)
        assert exc_info.value.field_name == "start_date"

        with raises(InvalidDateException) as exc_info:
            azm_resource.get_azm_timeseries_by_interval(start_date="2024-02-01", end_date="invalid")
        assert "invalid" in str(exc_info.value)
        assert exc_info.value.field_name == "end_date"

    def test_get_azm_timeseries_by_interval_exceeds_max_range(self, azm_resource):
        """Test that exceeding the 1095 day range limit raises InvalidDateRangeException"""
        start_date = (datetime.now() - timedelta(days=1096)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

        with raises(InvalidDateRangeException) as exc_info:
            azm_resource.get_azm_timeseries_by_interval(start_date=start_date, end_date=end_date)
        assert "1095 days" in str(exc_info.value)
        assert "AZM time series" in str(exc_info.value)

    def test_get_azm_timeseries_by_interval_invalid_date_order(self, azm_resource):
        """Test that start_date after end_date raises InvalidDateRangeException"""
        with raises(InvalidDateRangeException) as exc_info:
            azm_resource.get_azm_timeseries_by_interval(
                start_date="2025-02-02", end_date="2025-02-01"
            )
        assert "Start date 2025-02-02 is after end date 2025-02-01" in str(exc_info.value)

    def test_get_azm_timeseries_by_interval_with_user_id(self, azm_resource, mock_response):
        """Test getting AZM time series by date range for a specific user"""
        mock_response.json.return_value = {"activities-active-zone-minutes": []}
        azm_resource.oauth.request.return_value = mock_response

        result = azm_resource.get_azm_timeseries_by_interval(
            start_date="2025-02-01", end_date="2025-02-02", user_id="123ABC"
        )

        assert result == mock_response.json.return_value
        azm_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/123ABC/activities/active-zone-minutes/date/2025-02-01/2025-02-02.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_azm_timeseries_with_today_date(self, azm_resource, mock_response):
        """Test using 'today' as the date parameter"""
        mock_response.json.return_value = {"activities-active-zone-minutes": []}
        azm_resource.oauth.request.return_value = mock_response

        result = azm_resource.get_azm_timeseries_by_date(date="today")

        assert result == mock_response.json.return_value
        azm_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/today/1d.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_base_class_error_handling(self, azm_resource, mock_response_factory):
        """Test that base class error handling works correctly for both endpoints"""
        error_cases = [
            {
                "status_code": 401,
                "error_type": "invalid_token",
                "message": "Access token expired or invalid",
                "expected_exception": "InvalidTokenException",
            },
            {
                "status_code": 403,
                "error_type": "insufficient_scope",
                "message": "Insufficient scope to access this resource",
                "expected_exception": "InsufficientScopeException",
            },
            {
                "status_code": 400,
                "error_type": "validation",
                "message": "Invalid request parameters",
                "expected_exception": "ValidationException",
            },
            {
                "status_code": 500,
                "error_type": "system",
                "message": "Internal server error",
                "expected_exception": "SystemException",
            },
            {
                "status_code": 429,
                "error_type": "rate_limit_exceeded",
                "message": "Too many requests",
                "expected_exception": "RateLimitExceededException",
            },
            {
                "status_code": 404,
                "error_type": "not_found",
                "message": "Resource not found",
                "expected_exception": "NotFoundException",
            },
        ]

        for case in error_cases:
            error_response = mock_response_factory(
                case["status_code"],
                {"errors": [{"errorType": case["error_type"], "message": case["message"]}]},
            )
            azm_resource.oauth.request.return_value = error_response

            # Test errors for timeseries by date endpoint
            with raises(Exception) as exc_info:
                azm_resource.get_azm_timeseries_by_date(date="2025-02-01")
            assert case["expected_exception"] in str(exc_info.typename)

            # Test errors for timeseries by interval endpoint
            with raises(Exception) as exc_info:
                azm_resource.get_azm_timeseries_by_interval(
                    start_date="2025-02-01", end_date="2025-02-02"
                )
            assert case["expected_exception"] in str(exc_info.typename)
