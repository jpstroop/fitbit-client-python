# tests/resources/test_activity_timeseries.py

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.activity_timeseries import ActivityTimeSeriesResource
from fitbit_client.resources.constants import ActivityTimeSeriesPath
from fitbit_client.resources.constants import Period


class TestActivityTimeSeriesResource:
    @fixture
    def activity_resource(self, mock_oauth_session, mock_logger):
        """Fixture to provide an ActivityTimeSeriesResource instance with standard settings"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            resource = ActivityTimeSeriesResource(
                oauth_session=mock_oauth_session, locale="en_US", language="en_US"
            )
            return resource

    def test_get_time_series_by_date_success(self, activity_resource, mock_response):
        """Test successful retrieval of activity time series by date"""
        # Setup mock response
        mock_response.json.return_value = {
            "activities-steps": [{"dateTime": "2024-02-01", "value": "10000"}]
        }
        activity_resource.oauth.request.return_value = mock_response

        # Test the method
        result = activity_resource.get_time_series_by_date(
            resource_path=ActivityTimeSeriesPath.STEPS, date="2024-02-01", period=Period.ONE_DAY
        )

        # Verify the response
        assert result == {"activities-steps": [{"dateTime": "2024-02-01", "value": "10000"}]}

        # Verify the request was made correctly
        activity_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/activities/steps/date/2024-02-01/1d.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_time_series_activity_calories_range_limit(
        self, activity_resource, mock_response_factory
    ):
        """Test that activity calories respects the 30 day limit"""
        # Mock a 400 response for exceeding range
        error_response = mock_response_factory(
            400,
            {
                "errors": [
                    {
                        "errorType": "validation",
                        "message": (
                            "The range cannot exceed 31 days for resource type activityCalories"
                        ),
                    }
                ]
            },
        )
        activity_resource.oauth.request.return_value = error_response

        with raises(ValidationException) as exc_info:
            activity_resource.get_time_series_by_date_range(
                resource_path=ActivityTimeSeriesPath.ACTIVITY_CALORIES,
                start_date="2024-01-01",
                end_date="2024-02-15",  # More than 30 days
            )

        assert "31 days" in str(exc_info.value)

    def test_get_time_series_different_periods(self, activity_resource, mock_response):
        """Test getting time series with different period values"""
        mock_response.json.return_value = {"activities-steps": []}
        activity_resource.oauth.request.return_value = mock_response

        # Test each period type
        periods = [
            Period.ONE_DAY,
            Period.SEVEN_DAYS,
            Period.THIRTY_DAYS,
            Period.ONE_WEEK,
            Period.ONE_MONTH,
            Period.THREE_MONTHS,
            Period.SIX_MONTHS,
            Period.ONE_YEAR,
            Period.MAX,
        ]

        for period in periods:
            activity_resource.get_time_series_by_date(
                resource_path=ActivityTimeSeriesPath.STEPS, date="2024-02-01", period=period
            )

            expected_url = f"https://api.fitbit.com/1/user/-/activities/steps/date/2024-02-01/{period.value}.json"
            last_call = activity_resource.oauth.request.call_args_list[-1]
            assert last_call[0][1] == expected_url

    def test_calories_variants(self, activity_resource, mock_response):
        """Test different calorie measurement types return expected data"""
        mock_response.json.return_value = {
            "activities-activityCalories": [{"dateTime": "2024-02-01", "value": "300"}],
            "activities-calories": [{"dateTime": "2024-02-01", "value": "2000"}],
            "activities-caloriesBMR": [{"dateTime": "2024-02-01", "value": "1700"}],
        }
        activity_resource.oauth.request.return_value = mock_response

        # Test each calorie type
        calorie_types = [
            ActivityTimeSeriesPath.ACTIVITY_CALORIES,
            ActivityTimeSeriesPath.CALORIES,
            ActivityTimeSeriesPath.CALORIES_BMR,
            ActivityTimeSeriesPath.TRACKER_CALORIES,
            ActivityTimeSeriesPath.TRACKER_ACTIVITY_CALORIES,
        ]

        for calorie_type in calorie_types:
            result = activity_resource.get_time_series_by_date(
                resource_path=calorie_type, date="2024-02-01", period=Period.ONE_DAY
            )
            assert isinstance(result, dict)
            # Verify we get back numeric values for calories
            if result:  # Some responses might be empty but should still be dicts
                for entry in next(iter(result.values())):
                    assert entry["value"].isdigit()

    def test_get_time_series_by_date_with_user_id(self, activity_resource, mock_response):
        """Test getting time series for a specific user"""
        mock_response.json.return_value = {"activities-steps": []}
        activity_resource.oauth.request.return_value = mock_response

        result = activity_resource.get_time_series_by_date(
            resource_path=ActivityTimeSeriesPath.STEPS,
            date="2024-02-01",
            period=Period.ONE_DAY,
            user_id="123ABC",
        )

        activity_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/123ABC/activities/steps/date/2024-02-01/1d.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_time_series_by_date_range_success(self, activity_resource, mock_response):
        """Test successful retrieval of activity time series by date range"""
        mock_response.json.return_value = {
            "activities-steps": [
                {"dateTime": "2024-02-01", "value": "10000"},
                {"dateTime": "2024-02-02", "value": "12000"},
            ]
        }
        activity_resource.oauth.request.return_value = mock_response

        result = activity_resource.get_time_series_by_date_range(
            resource_path=ActivityTimeSeriesPath.STEPS,
            start_date="2024-02-01",
            end_date="2024-02-02",
        )

        assert result == {
            "activities-steps": [
                {"dateTime": "2024-02-01", "value": "10000"},
                {"dateTime": "2024-02-02", "value": "12000"},
            ]
        }

        activity_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/activities/steps/date/2024-02-01/2024-02-02.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_time_series_by_date_range_with_user_id(self, activity_resource, mock_response):
        """Test getting time series by date range for a specific user"""
        mock_response.json.return_value = {"activities-steps": []}
        activity_resource.oauth.request.return_value = mock_response

        result = activity_resource.get_time_series_by_date_range(
            resource_path=ActivityTimeSeriesPath.STEPS,
            start_date="2024-02-01",
            end_date="2024-02-02",
            user_id="123ABC",
        )

        activity_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/123ABC/activities/steps/date/2024-02-01/2024-02-02.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_time_series_by_date_tracker_only(self, activity_resource, mock_response):
        """Test getting tracker-only activity data"""
        mock_response.json.return_value = {"activities-tracker-steps": []}
        activity_resource.oauth.request.return_value = mock_response

        result = activity_resource.get_time_series_by_date(
            resource_path=ActivityTimeSeriesPath.TRACKER_STEPS,
            date="2024-02-01",
            period=Period.ONE_DAY,
        )

        activity_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/activities/tracker/steps/date/2024-02-01/1d.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_time_series_with_today_date(self, activity_resource, mock_response):
        """Test using 'today' as the date parameter"""
        mock_response.json.return_value = {"activities-steps": []}
        activity_resource.oauth.request.return_value = mock_response

        result = activity_resource.get_time_series_by_date(
            resource_path=ActivityTimeSeriesPath.STEPS, date="today", period=Period.ONE_DAY
        )

        activity_resource.oauth.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/activities/steps/date/today/1d.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )
