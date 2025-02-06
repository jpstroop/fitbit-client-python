# tests/resources/test_sleep.py

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException
from fitbit_client.resources.sleep import SleepResource


class TestSleepResource:
    @fixture
    def sleep_resource(self, mock_oauth_session, mock_logger):
        """Create SleepResource instance with mocked dependencies"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return SleepResource(mock_oauth_session, "en_US", "en_US")

    def test_create_sleep_goals_success(
        self, sleep_resource, mock_oauth_session, mock_response_factory
    ):
        """Test successful creation of sleep goal"""
        mock_response = mock_response_factory(200, {"goal": {"minDuration": 480}})
        mock_oauth_session.request.return_value = mock_response

        result = sleep_resource.create_sleep_goals(min_duration=480)

        assert result["goal"]["minDuration"] == 480
        mock_oauth_session.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1.2/user/-/sleep/goal.json",
            data={"minDuration": 480},
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_create_sleep_goals_invalid_duration(self, sleep_resource):
        """Test that negative duration raises ValueError"""
        with raises(ValueError) as exc_info:
            sleep_resource.create_sleep_goals(min_duration=-1)
        assert "min_duration must be positive" in str(exc_info.value)

    def test_create_sleep_log_success(
        self, sleep_resource, mock_oauth_session, mock_response_factory
    ):
        """Test successful creation of sleep log entry"""
        expected_response = {
            "sleep": [{"logId": 123, "startTime": "22:00", "duration": 28800000}]
        }  # 8 hours in milliseconds
        mock_response = mock_response_factory(200, expected_response)
        mock_oauth_session.request.return_value = mock_response

        result = sleep_resource.create_sleep_log(
            start_time="22:00", duration_millis=28800000, date="2024-02-13"
        )

        assert result == expected_response
        mock_oauth_session.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1.2/user/-/sleep.json",
            data=None,
            json=None,
            params={"startTime": "22:00", "duration": 28800000, "date": "2024-02-13"},
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_create_sleep_log_invalid_duration(self, sleep_resource):
        """Test that negative duration raises ValueError"""
        with raises(ValueError) as exc_info:
            sleep_resource.create_sleep_log(
                start_time="22:00", duration_millis=-1, date="2024-02-13"
            )
        assert "duration_millis must be positive" in str(exc_info.value)

    def test_create_sleep_log_invalid_date(self, sleep_resource):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException):
            sleep_resource.create_sleep_log(
                start_time="22:00", duration_millis=28800000, date="invalid-date"
            )

    def test_create_sleep_log_allows_today(
        self, sleep_resource, mock_oauth_session, mock_response_factory
    ):
        """Test that 'today' is accepted as a valid date"""
        mock_response = mock_response_factory(200, {"sleep": [{"logId": 123}]})
        mock_oauth_session.request.return_value = mock_response

        # Should not raise an exception
        sleep_resource.create_sleep_log(start_time="22:00", duration_millis=28800000, date="today")

    def test_delete_sleep_log_success(
        self, sleep_resource, mock_oauth_session, mock_response_factory
    ):
        """Test successful deletion of sleep log"""
        mock_response = mock_response_factory(204, None)
        mock_oauth_session.request.return_value = mock_response

        result = sleep_resource.delete_sleep_log(log_id="123")

        assert result is None
        mock_oauth_session.request.assert_called_once_with(
            "DELETE",
            "https://api.fitbit.com/1.2/user/-/sleep/123.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_sleep_goals_success(
        self, sleep_resource, mock_oauth_session, mock_response_factory
    ):
        """Test successful retrieval of sleep goals"""
        expected_response = {
            "goal": {"minDuration": 480, "consistency": "ACTIVE", "updatedOn": "2024-02-13"}
        }
        mock_response = mock_response_factory(200, expected_response)
        mock_oauth_session.request.return_value = mock_response

        result = sleep_resource.get_sleep_goals()

        assert result == expected_response
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1.2/user/-/sleep/goal.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_sleep_log_by_date_success(
        self, sleep_resource, mock_oauth_session, mock_response_factory
    ):
        """Test successful retrieval of sleep log by date"""
        expected_response = {
            "sleep": [{"dateOfSleep": "2024-02-13", "duration": 28800000, "efficiency": 90}]
        }
        mock_response = mock_response_factory(200, expected_response)
        mock_oauth_session.request.return_value = mock_response

        result = sleep_resource.get_sleep_log_by_date("2024-02-13")

        assert result == expected_response
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1.2/user/-/sleep/date/2024-02-13.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_sleep_log_by_date_invalid_date(self, sleep_resource):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException):
            sleep_resource.get_sleep_log_by_date("invalid-date")

    def test_get_sleep_log_by_date_allows_today(
        self, sleep_resource, mock_oauth_session, mock_response_factory
    ):
        """Test that 'today' is accepted as a valid date"""
        mock_response = mock_response_factory(200, {"sleep": []})
        mock_oauth_session.request.return_value = mock_response

        # Should not raise an exception
        sleep_resource.get_sleep_log_by_date("today")

    def test_get_sleep_log_by_date_range_success(
        self, sleep_resource, mock_oauth_session, mock_response_factory
    ):
        """Test successful retrieval of sleep log by date range"""
        expected_response = {
            "sleep": [
                {"dateOfSleep": "2024-02-13", "duration": 28800000},
                {"dateOfSleep": "2024-02-14", "duration": 27000000},
            ]
        }
        mock_response = mock_response_factory(200, expected_response)
        mock_oauth_session.request.return_value = mock_response

        result = sleep_resource.get_sleep_log_by_date_range("2024-02-13", "2024-02-14")

        assert result == expected_response
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1.2/user/-/sleep/date/2024-02-13/2024-02-14.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_sleep_log_by_date_range_invalid_dates(self, sleep_resource):
        """Test that invalid date formats raise InvalidDateException"""
        with raises(InvalidDateException):
            sleep_resource.get_sleep_log_by_date_range("invalid", "2024-02-14")

        with raises(InvalidDateException):
            sleep_resource.get_sleep_log_by_date_range("2024-02-13", "invalid")

    def test_get_sleep_log_by_date_range_invalid_range(self, sleep_resource):
        """Test that end date before start date raises InvalidDateRangeException"""
        with raises(InvalidDateRangeException):
            sleep_resource.get_sleep_log_by_date_range("2024-02-14", "2024-02-13")

    def test_get_sleep_log_by_date_range_exceeds_max_days(self, sleep_resource):
        """Test that exceeding 100 days raises InvalidDateRangeException"""
        with raises(InvalidDateRangeException) as exc_info:
            sleep_resource.get_sleep_log_by_date_range(
                "2024-02-13", "2024-05-24"
            )  # More than 100 days
        assert "Date range 2024-02-13 to 2024-05-24 exceeds maximum allowed 100 days" in str(
            exc_info.value
        )

    def test_get_sleep_log_by_date_range_allows_today(
        self, sleep_resource, mock_oauth_session, mock_response_factory
    ):
        """Test that 'today' is accepted in date range"""
        mock_response = mock_response_factory(200, {"sleep": []})
        mock_oauth_session.request.return_value = mock_response

        # Should not raise an exception
        sleep_resource.get_sleep_log_by_date_range("today", "today")

    def test_get_sleep_log_list_success(
        self, sleep_resource, mock_oauth_session, mock_response_factory
    ):
        """Test successful retrieval of sleep log list"""
        expected_response = {
            "sleep": [{"dateOfSleep": "2024-02-13"}],
            "pagination": {"next": "", "previous": ""},
        }
        mock_response = mock_response_factory(200, expected_response)
        mock_oauth_session.request.return_value = mock_response

        result = sleep_resource.get_sleep_log_list(before_date="2024-02-13")

        assert result == expected_response
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1.2/user/-/sleep/list.json",
            data=None,
            json=None,
            params={"sort": "desc", "limit": 100, "offset": 0, "beforeDate": "2024-02-13"},
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_sleep_log_list_invalid_dates(self, sleep_resource):
        """Test that invalid date formats raise InvalidDateException"""
        with raises(InvalidDateException):
            sleep_resource.get_sleep_log_list(before_date="invalid")

        with raises(InvalidDateException):
            sleep_resource.get_sleep_log_list(after_date="invalid")

    def test_get_sleep_log_list_missing_dates(self, sleep_resource):
        """Test that omitting both dates raises ValueError"""
        with raises(ValueError) as exc_info:
            sleep_resource.get_sleep_log_list()
        assert "Must specify either before_date or after_date" in str(exc_info.value)

    def test_get_sleep_log_list_invalid_limit(self, sleep_resource):
        """Test that exceeding max limit raises ValueError"""
        with raises(ValueError) as exc_info:
            sleep_resource.get_sleep_log_list(before_date="2024-02-13", limit=101)
        assert "Maximum limit is 100" in str(exc_info.value)

    def test_get_sleep_log_list_invalid_sort(self, sleep_resource):
        """Test that invalid sort value raises ValueError"""
        with raises(ValueError) as exc_info:
            sleep_resource.get_sleep_log_list(before_date="2024-02-13", sort="invalid")
        assert "Sort must be either 'asc' or 'desc'" in str(exc_info.value)

    def test_get_sleep_log_list_mismatched_sort_direction(self, sleep_resource):
        """Test validation of sort direction matching date parameter"""
        with raises(ValueError) as exc_info:
            sleep_resource.get_sleep_log_list(before_date="2024-02-13", sort="asc")
        assert "Must use sort='desc' with before_date" in str(exc_info.value)

        with raises(ValueError) as exc_info:
            sleep_resource.get_sleep_log_list(after_date="2024-02-13", sort="desc")
        assert "Must use sort='asc' with after_date" in str(exc_info.value)

    def test_get_sleep_log_list_allows_today(
        self, sleep_resource, mock_oauth_session, mock_response_factory
    ):
        """Test that 'today' is accepted for date parameters"""
        mock_response = mock_response_factory(200, {"sleep": []})
        mock_oauth_session.request.return_value = mock_response

        # Should not raise exceptions
        sleep_resource.get_sleep_log_list(before_date="today", sort="desc")
        sleep_resource.get_sleep_log_list(after_date="today", sort="asc")
