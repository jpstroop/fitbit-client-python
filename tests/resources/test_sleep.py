# tests/resources/test_sleep.py

# Standard library imports
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.resources.constants import SleepType
from fitbit_client.resources.sleep import SleepResource

# tests/resources/test_sleep.py


# tests/resources/test_sleep.py


class TestSleepResource:
    @fixture
    def mock_oauth_session(self):
        """Fixture to provide a mock OAuth session"""
        return Mock()

    @fixture
    def mock_response(self):
        """Fixture to provide a mock response"""
        response = Mock()
        response.status_code = 200  # Set default status code
        return response

    @fixture
    def mock_logger(self):
        """Fixture to provide a mock logger"""
        return Mock()

    @fixture
    def sleep_resource(self, mock_oauth_session, mock_logger):
        """Fixture to provide a SleepResource instance"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return SleepResource(oauth_session=mock_oauth_session, locale="en_US", language="en_US")

    def test_create_sleep_goal(self, sleep_resource, mock_oauth_session, mock_response):
        """Test creating a sleep goal"""
        mock_response.json.return_value = {"success": True}
        mock_response.headers = {"content-type": "application/json"}
        mock_oauth_session.request.return_value = mock_response

        result = sleep_resource.create_sleep_goal(480)  # 8 hours

        assert result == {"success": True}
        mock_oauth_session.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1.2/user/-/sleep/goal.json",
            data={"minDuration": 480},
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_create_sleep_goal_invalid_duration(self, sleep_resource):
        """Test creating a sleep goal with invalid duration"""
        with raises(ValueError, match="min_duration must be positive"):
            sleep_resource.create_sleep_goal(0)

    def test_log_sleep(self, sleep_resource, mock_oauth_session, mock_response):
        """Test logging a sleep entry"""
        mock_response.json.return_value = {"success": True}
        mock_response.headers = {"content-type": "application/json"}
        mock_oauth_session.request.return_value = mock_response

        result = sleep_resource.log_sleep(
            start_time="23:00", duration_millis=28800000, date="2025-01-31"  # 8 hours
        )

        assert result == {"success": True}
        mock_oauth_session.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1.2/user/-/sleep.json",
            data=None,
            json=None,
            params={
                "startTime": "23:00",
                "duration": 28800000,
                "date": "2025-01-31",
                "type": "classic",
            },
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_log_sleep_with_type(self, sleep_resource, mock_oauth_session, mock_response):
        """Test logging a sleep entry with specified type"""
        mock_response.json.return_value = {"success": True}
        mock_response.headers = {"content-type": "application/json"}
        mock_oauth_session.request.return_value = mock_response

        result = sleep_resource.log_sleep(
            start_time="23:00",
            duration_millis=28800000,
            date="2025-01-31",
            sleep_type=SleepType.STAGES,
        )

        assert result == {"success": True}
        assert mock_oauth_session.request.call_args[1]["params"]["type"] == "stages"

    def test_log_sleep_invalid_duration(self, sleep_resource):
        """Test logging sleep with invalid duration"""
        with raises(ValueError, match="duration_millis must be positive"):
            sleep_resource.log_sleep(start_time="23:00", duration_millis=0, date="2025-01-31")

    def test_delete_sleep_log(self, sleep_resource, mock_oauth_session, mock_response):
        """Test deleting a sleep log"""
        mock_response.status_code = 204
        mock_oauth_session.request.return_value = mock_response

        result = sleep_resource.delete_sleep_log("123456")

        assert result is None
        mock_oauth_session.request.assert_called_once_with(
            "DELETE",
            "https://api.fitbit.com/1.2/user/-/sleep/123456.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_sleep_goal(self, sleep_resource, mock_oauth_session, mock_response):
        """Test getting sleep goal"""
        mock_response.json.return_value = {
            "minDuration": 480,
            "consistency": "ACTIVE",
            "updatedOn": "2025-01-31",
        }
        mock_response.headers = {"content-type": "application/json"}
        mock_oauth_session.request.return_value = mock_response

        result = sleep_resource.get_sleep_goal()

        assert result["minDuration"] == 480
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1.2/user/-/sleep/goal.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_sleep_log_by_date(self, sleep_resource, mock_oauth_session, mock_response):
        """Test getting sleep logs for a date"""
        mock_response.json.return_value = {"sleep": []}
        mock_response.headers = {"content-type": "application/json"}
        mock_oauth_session.request.return_value = mock_response

        result = sleep_resource.get_sleep_log_by_date("2025-01-31")

        assert "sleep" in result
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1.2/user/-/sleep/date/2025-01-31.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_sleep_log_by_date_range(self, sleep_resource, mock_oauth_session, mock_response):
        """Test getting sleep logs for a date range"""
        mock_response.json.return_value = {"sleep": []}
        mock_response.headers = {"content-type": "application/json"}
        mock_oauth_session.request.return_value = mock_response

        result = sleep_resource.get_sleep_log_by_date_range("2025-01-01", "2025-01-31")

        assert "sleep" in result
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1.2/user/-/sleep/date/2025-01-01/2025-01-31.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_sleep_log_list(self, sleep_resource, mock_oauth_session, mock_response):
        """Test getting list of sleep logs"""
        mock_response.json.return_value = {"sleep": []}
        mock_response.headers = {"content-type": "application/json"}
        mock_oauth_session.request.return_value = mock_response

        result = sleep_resource.get_sleep_log_list(before_date="2025-01-31")

        assert "sleep" in result
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1.2/user/-/sleep/list.json",
            data=None,
            json=None,
            params={"sort": "desc", "limit": 100, "offset": 0, "beforeDate": "2025-01-31"},
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_sleep_log_list_missing_date(self, sleep_resource):
        """Test getting list of sleep logs without required date parameter"""
        with raises(ValueError, match="Must specify either before_date or after_date"):
            sleep_resource.get_sleep_log_list()

    def test_get_sleep_log_list_invalid_limit(self, sleep_resource):
        """Test getting list of sleep logs with invalid limit"""
        with raises(ValueError, match="Maximum limit is 100"):
            sleep_resource.get_sleep_log_list(before_date="2025-01-31", limit=101)

    def test_get_sleep_log_list_invalid_sort(self, sleep_resource):
        """Test getting list of sleep logs with invalid sort"""
        with raises(ValueError, match="Sort must be either 'asc' or 'desc'"):
            sleep_resource.get_sleep_log_list(before_date="2025-01-31", sort="invalid")

    def test_get_sleep_log_list_before_date_wrong_sort(self, sleep_resource):
        """Test getting list of sleep logs with before_date and wrong sort direction"""
        with raises(ValueError, match="Must use sort='desc' with before_date"):
            sleep_resource.get_sleep_log_list(before_date="2025-01-31", sort="asc")

    def test_get_sleep_log_list_after_date_wrong_sort(self, sleep_resource):
        """Test getting list of sleep logs with after_date and wrong sort direction"""
        with raises(ValueError, match="Must use sort='asc' with after_date"):
            sleep_resource.get_sleep_log_list(after_date="2025-01-31", sort="desc")

    def test_get_sleep_log_list_after_date(self, sleep_resource, mock_oauth_session, mock_response):
        """Test getting list of sleep logs with after_date"""
        mock_response.json.return_value = {"sleep": []}
        mock_response.headers = {"content-type": "application/json"}
        mock_oauth_session.request.return_value = mock_response

        result = sleep_resource.get_sleep_log_list(after_date="2025-01-01", sort="asc")

        assert "sleep" in result
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1.2/user/-/sleep/list.json",
            data=None,
            json=None,
            params={"sort": "asc", "limit": 100, "offset": 0, "afterDate": "2025-01-01"},
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )
