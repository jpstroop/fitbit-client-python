# tests/resources/test_activity.py

# Standard library imports
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.activity import ActivityResource
from fitbit_client.resources.constants import ActivityGoalPeriod
from fitbit_client.resources.constants import ActivityGoalType


class TestActivityResource:

    @fixture
    def activity_resource(self, mock_oauth_session, mock_logger):
        """Create an ActivityResource with mocked OAuth session"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return ActivityResource(mock_oauth_session, "en_US", "en_US")

    def test_create_activity_goals(self, activity_resource):
        """Test creating activity goal"""
        activity_resource._make_request = Mock()
        activity_resource.create_activity_goals(
            period=ActivityGoalPeriod.DAILY, type=ActivityGoalType.STEPS, value=10000
        )

        activity_resource._make_request.assert_called_once_with(
            "activities/goals/daily.json",
            params={"type": "steps", "value": 10000},
            user_id="-",
            http_method="POST",
            debug=False,
        )

    def test_create_activity_log_with_activity_id_only(self, activity_resource):
        """Test creating activity log with just an activity ID"""
        activity_resource._make_request = Mock()
        activity_resource.create_activity_log(
            activity_id=123, start_time="12:00", duration_millis=3600000, date="2023-01-01"
        )

        expected_params = {
            "activityId": 123,
            "startTime": "12:00",
            "durationMillis": 3600000,
            "date": "2023-01-01",
        }
        activity_resource._make_request.assert_called_once_with(
            "activities.json", params=expected_params, user_id="-", http_method="POST", debug=False
        )

    def test_create_activity_log_invalid_date(self, activity_resource):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException) as exc_info:
            activity_resource.create_activity_log(
                activity_id=123, start_time="12:00", duration_millis=3600000, date="invalid-date"
            )
        assert "invalid-date" in str(exc_info.value)
        assert exc_info.value.field_name == "date"

    def test_create_activity_log_with_distance_no_unit(self, activity_resource):
        """Test creating activity log with distance but no distance unit"""
        activity_resource._make_request = Mock()
        activity_resource.create_activity_log(
            activity_id=123,
            start_time="12:00",
            duration_millis=3600000,
            date="2023-01-01",
            distance=5.0,
        )

        expected_params = {
            "activityId": 123,
            "startTime": "12:00",
            "durationMillis": 3600000,
            "date": "2023-01-01",
            "distance": 5.0,
        }
        activity_resource._make_request.assert_called_once_with(
            "activities.json", params=expected_params, user_id="-", http_method="POST", debug=False
        )

    def test_get_activity_log_list_invalid_dates(self, activity_resource):
        """Test invalid dates in get_activity_log_list"""
        with raises(InvalidDateException) as exc_info:
            activity_resource.get_activity_log_list(before_date="invalid-date")
        assert "invalid-date" in str(exc_info.value)
        assert exc_info.value.field_name == "before_date"

        with raises(InvalidDateException) as exc_info:
            activity_resource.get_activity_log_list(after_date="invalid-date")
        assert "invalid-date" in str(exc_info.value)
        assert exc_info.value.field_name == "after_date"

    def test_get_activity_log_list_validates_limit(self, activity_resource):
        """Test that exceeding max limit raises ValidationException"""
        with raises(ValidationException) as exc_info:
            activity_resource.get_activity_log_list(limit=101)

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "limit"
        assert "Maximum limit is 100" in str(exc_info.value)

    def test_get_activity_log_list_validates_sort_order(self, activity_resource):
        """Test that invalid sort order raises ValidationException"""
        with raises(ValidationException) as exc_info:
            activity_resource.get_activity_log_list(sort="invalid")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "sort"
        assert "Sort must be either" in str(exc_info.value)

    def test_get_activity_log_list_accepts_valid_limit(self, activity_resource):
        """Test that valid limit is accepted"""
        activity_resource._make_request = Mock()
        activity_resource.get_activity_log_list(limit=100)
        activity_resource._make_request.assert_called_once()

        activity_resource._make_request = Mock()
        activity_resource.get_activity_log_list(limit=50)
        activity_resource._make_request.assert_called_once()

    def test_get_activity_log_list_accepts_valid_sort(self, activity_resource):
        """Test that valid sort orders are accepted"""
        activity_resource._make_request = Mock()
        activity_resource.get_activity_log_list(sort="asc")
        activity_resource._make_request.assert_called_once()

        activity_resource._make_request = Mock()
        activity_resource.get_activity_log_list(sort="desc")
        activity_resource._make_request.assert_called_once()

    def test_get_activity_log_list_parameters(self, activity_resource):
        """Test that parameters are correctly passed to request"""
        activity_resource._make_request = Mock()
        activity_resource.get_activity_log_list(
            before_date="2023-01-01", after_date="2022-12-01", sort="desc", limit=50, offset=10
        )

        activity_resource._make_request.assert_called_once_with(
            "activities/list.json",
            params={
                "sort": "desc",
                "limit": 50,
                "offset": 10,
                "beforeDate": "2023-01-01",
                "afterDate": "2022-12-01",
            },
            user_id="-",
            debug=False,
        )

    def test_create_favorite_activity(self, activity_resource):
        """Test creating favorite activity"""
        activity_resource._make_request = Mock()
        activity_resource.create_favorite_activity("123")
        activity_resource._make_request.assert_called_once_with(
            "activities/favorite/123.json", user_id="-", http_method="POST", debug=False
        )

    def test_delete_activity_log(self, activity_resource):
        """Test deleting activity log"""
        activity_resource._make_request = Mock()
        activity_resource.delete_activity_log("123")
        activity_resource._make_request.assert_called_once_with(
            "activities/123.json", user_id="-", http_method="DELETE", debug=False
        )

    def test_delete_favorite_activity(self, activity_resource):
        """Test deleting favorite activity"""
        activity_resource._make_request = Mock()
        activity_resource.delete_favorite_activity("123")
        activity_resource._make_request.assert_called_once_with(
            "activities/favorite/123.json", user_id="-", http_method="DELETE", debug=False
        )

    def test_get_activity_goals(self, activity_resource):
        """Test getting activity goals"""
        activity_resource._make_request = Mock()
        activity_resource.get_activity_goals(ActivityGoalPeriod.DAILY)
        activity_resource._make_request.assert_called_once_with(
            "activities/goals/daily.json", user_id="-", debug=False
        )

    def test_get_daily_activity_summary_invalid_date(self, activity_resource):
        """Test that invalid date format raises InvalidDateException"""
        with raises(InvalidDateException) as exc_info:
            activity_resource.get_daily_activity_summary("invalid-date")
        assert "invalid-date" in str(exc_info.value)
        assert exc_info.value.field_name == "date"

    def test_get_daily_activity_summary_success(self, activity_resource):
        """Test getting daily activity summary"""
        activity_resource._make_request = Mock()
        activity_resource.get_daily_activity_summary("2023-01-01")
        activity_resource._make_request.assert_called_once_with(
            "activities/date/2023-01-01.json", user_id="-", debug=False
        )

    def test_get_activity_type(self, activity_resource):
        """Test getting activity type"""
        activity_resource._make_request = Mock()
        activity_resource.get_activity_type("123")
        activity_resource._make_request.assert_called_once_with(
            "activities/123.json", requires_user_id=False, debug=False
        )

    def test_get_all_activity_types(self, activity_resource):
        """Test getting all activity types"""
        activity_resource._make_request = Mock()
        activity_resource.get_all_activity_types()
        activity_resource._make_request.assert_called_once_with(
            "activities.json", requires_user_id=False, debug=False
        )

    def test_get_favorite_activities(self, activity_resource):
        """Test getting favorite activities"""
        activity_resource._make_request = Mock()
        activity_resource.get_favorite_activities()
        activity_resource._make_request.assert_called_once_with(
            "activities/favorite.json", user_id="-", debug=False
        )

    def test_get_frequent_activities(self, activity_resource):
        """Test getting frequent activities"""
        activity_resource._make_request = Mock()
        activity_resource.get_frequent_activities()
        activity_resource._make_request.assert_called_once_with(
            "activities/frequent.json", user_id="-", debug=False
        )

    def test_get_recent_activity_types(self, activity_resource):
        """Test getting recent activities"""
        activity_resource._make_request = Mock()
        activity_resource.get_recent_activity_types()
        activity_resource._make_request.assert_called_once_with(
            "activities/recent.json", user_id="-", debug=False
        )

    def test_get_lifetime_stats(self, activity_resource):
        """Test getting lifetime stats"""
        activity_resource._make_request = Mock()
        activity_resource.get_lifetime_stats()
        activity_resource._make_request.assert_called_once_with(
            "activities.json", user_id="-", debug=False
        )

    def test_get_activity_tcx(self, activity_resource):
        """Test getting activity TCX data"""
        activity_resource._make_request = Mock()

        # Test without partial TCX
        activity_resource.get_activity_tcx(123)
        activity_resource._make_request.assert_called_once_with(
            "activities/123.tcx", params=None, user_id="-", debug=False
        )

        # Test with partial TCX
        activity_resource._make_request = Mock()
        activity_resource.get_activity_tcx("123", include_partial_tcx=True)
        activity_resource._make_request.assert_called_once_with(
            "activities/123.tcx", params={"includePartialTCX": True}, user_id="-", debug=False
        )
