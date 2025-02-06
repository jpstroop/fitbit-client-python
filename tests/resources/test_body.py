# tests/resources/test_body.py

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.resources.body import BodyResource
from fitbit_client.resources.constants import BodyGoalType


class TestBodyResource:
    @fixture
    def body_resource(self, mock_oauth_session, mock_logger):
        """Create BodyResource instance with mocked OAuth session"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return BodyResource(mock_oauth_session, "en_US", "en_US")

    def test_create_bodyfat_goal(self, body_resource, mock_oauth_session, mock_response_factory):
        """Test creating a body fat goal"""
        mock_response = mock_response_factory(201, {"goal": {"fat": 25}})
        mock_oauth_session.request.return_value = mock_response

        result = body_resource.create_bodyfat_goal(fat=25.0)

        mock_oauth_session.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1/user/-/body/log/fat/goal.json",
            data=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
            json=None,
            params={"fat": 25.0},
        )
        assert result["goal"]["fat"] == 25

    def test_create_bodyfat_log_with_time(
        self, body_resource, mock_oauth_session, mock_response_factory
    ):
        """Test creating a body fat log entry with time parameter"""
        mock_response = mock_response_factory(
            201,
            {
                "fatLog": {
                    "date": "2024-02-10",
                    "fat": 15,
                    "logId": 1553069700000,
                    "source": "api",
                    "time": "08:15:00",
                }
            },
        )
        mock_oauth_session.request.return_value = mock_response

        result = body_resource.create_bodyfat_log(fat=15.0, date="2024-02-10", time="08:15:00")

        mock_oauth_session.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1/user/-/body/log/fat.json",
            data=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
            json=None,
            params={"fat": 15.0, "date": "2024-02-10", "time": "08:15:00"},
        )
        assert result["fatLog"]["logId"] == 1553069700000

    def test_create_bodyfat_log_without_time(
        self, body_resource, mock_oauth_session, mock_response_factory
    ):
        """Test creating a body fat log entry without time parameter"""
        mock_response = mock_response_factory(
            201,
            {
                "fatLog": {
                    "date": "2024-02-10",
                    "fat": 15,
                    "logId": 1553069700000,
                    "source": "api",
                    "time": "23:59:59",
                }
            },
        )
        mock_oauth_session.request.return_value = mock_response

        result = body_resource.create_bodyfat_log(fat=15.0, date="2024-02-10")

        mock_oauth_session.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1/user/-/body/log/fat.json",
            data=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
            json=None,
            params={"fat": 15.0, "date": "2024-02-10"},
        )
        assert result["fatLog"]["logId"] == 1553069700000

    def test_create_weight_goal_with_weight(
        self, body_resource, mock_oauth_session, mock_response_factory
    ):
        """Test creating a weight goal with weight parameter"""
        mock_response = mock_response_factory(
            201,
            {
                "goal": {
                    "goalType": "LOSE",
                    "startDate": "2024-02-10",
                    "startWeight": 200,
                    "weight": 180.5,
                    "weightThreshold": 0.05,
                }
            },
        )
        mock_oauth_session.request.return_value = mock_response

        result = body_resource.create_weight_goal(
            start_date="2024-02-10", start_weight=200, weight=180.5
        )

        mock_oauth_session.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1/user/-/body/log/weight/goal.json",
            data=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
            json=None,
            params={"startDate": "2024-02-10", "startWeight": 200, "weight": 180.5},
        )
        assert result["goal"]["weight"] == 180.5

    def test_create_weight_goal_without_weight(
        self, body_resource, mock_oauth_session, mock_response_factory
    ):
        """Test creating a weight goal without weight parameter"""
        mock_response = mock_response_factory(
            201,
            {
                "goal": {
                    "goalType": "LOSE",
                    "startDate": "2024-02-10",
                    "startWeight": 200,
                    "weightThreshold": 0.05,
                }
            },
        )
        mock_oauth_session.request.return_value = mock_response

        result = body_resource.create_weight_goal(start_date="2024-02-10", start_weight=200)

        mock_oauth_session.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1/user/-/body/log/weight/goal.json",
            data=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
            json=None,
            params={"startDate": "2024-02-10", "startWeight": 200},
        )
        assert result["goal"]["startWeight"] == 200

    def test_create_weight_log_with_time(
        self, body_resource, mock_oauth_session, mock_response_factory
    ):
        """Test creating a weight log entry with time parameter"""
        mock_response = mock_response_factory(
            201,
            {
                "weightLog": {
                    "bmi": 25.91,
                    "date": "2024-02-10",
                    "logId": 1553067494000,
                    "source": "api",
                    "time": "07:38:14",
                    "weight": 200,
                }
            },
        )
        mock_oauth_session.request.return_value = mock_response

        result = body_resource.create_weight_log(weight=200, date="2024-02-10", time="07:38:14")

        mock_oauth_session.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1/user/-/body/log/weight.json",
            data=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
            json=None,
            params={"weight": 200, "date": "2024-02-10", "time": "07:38:14"},
        )
        assert result["weightLog"]["logId"] == 1553067494000

    def test_create_weight_log_without_time(
        self, body_resource, mock_oauth_session, mock_response_factory
    ):
        """Test creating a weight log entry without time parameter"""
        mock_response = mock_response_factory(
            201,
            {
                "weightLog": {
                    "bmi": 25.91,
                    "date": "2024-02-10",
                    "logId": 1553067494000,
                    "source": "api",
                    "time": "23:59:59",
                    "weight": 200,
                }
            },
        )
        mock_oauth_session.request.return_value = mock_response

        result = body_resource.create_weight_log(weight=200, date="2024-02-10")

        mock_oauth_session.request.assert_called_once_with(
            "POST",
            "https://api.fitbit.com/1/user/-/body/log/weight.json",
            data=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
            json=None,
            params={"weight": 200, "date": "2024-02-10"},
        )
        assert result["weightLog"]["logId"] == 1553067494000

    def test_delete_bodyfat_log(self, body_resource, mock_oauth_session, mock_response_factory):
        """Test deleting a body fat log entry"""
        mock_response = mock_response_factory(204)
        mock_oauth_session.request.return_value = mock_response

        result = body_resource.delete_bodyfat_log("1553069700000")

        mock_oauth_session.request.assert_called_once_with(
            "DELETE",
            "https://api.fitbit.com/1/user/-/body/log/fat/1553069700000.json",
            data=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
            json=None,
            params=None,
        )
        assert result is None

    def test_delete_weight_log(self, body_resource, mock_oauth_session, mock_response_factory):
        """Test deleting a weight log entry"""
        mock_response = mock_response_factory(204)
        mock_oauth_session.request.return_value = mock_response

        result = body_resource.delete_weight_log("1553067494000")

        mock_oauth_session.request.assert_called_once_with(
            "DELETE",
            "https://api.fitbit.com/1/user/-/body/log/weight/1553067494000.json",
            data=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
            json=None,
            params=None,
        )
        assert result is None

    def test_get_body_goals_fat(self, body_resource, mock_oauth_session, mock_response_factory):
        """Test getting body fat goals"""
        mock_response = mock_response_factory(200, {"goal": {"fat": 25}})
        mock_oauth_session.request.return_value = mock_response

        result = body_resource.get_body_goals(BodyGoalType.FAT)

        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/body/log/fat/goal.json",
            data=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
            json=None,
            params=None,
        )
        assert result["goal"]["fat"] == 25

    def test_get_body_goals_weight(self, body_resource, mock_oauth_session, mock_response_factory):
        """Test getting weight goals"""
        mock_response = mock_response_factory(
            200,
            {
                "goal": {
                    "goalType": "LOSE",
                    "startDate": "2024-02-10",
                    "startWeight": 200,
                    "weight": 180.5,
                    "weightThreshold": 0.05,
                }
            },
        )
        mock_oauth_session.request.return_value = mock_response

        result = body_resource.get_body_goals(BodyGoalType.WEIGHT)

        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/body/log/weight/goal.json",
            data=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
            json=None,
            params=None,
        )
        assert result["goal"]["goalType"] == "LOSE"

    def test_get_bodyfat_log(self, body_resource, mock_oauth_session, mock_response_factory):
        """Test getting body fat logs for a date"""
        mock_response = mock_response_factory(
            200,
            {
                "fat": [
                    {
                        "date": "2024-02-10",
                        "fat": 15,
                        "logId": 1553067000000,
                        "source": "api",
                        "time": "07:38:14",
                    }
                ]
            },
        )
        mock_oauth_session.request.return_value = mock_response

        result = body_resource.get_bodyfat_log("2024-02-10")

        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/body/log/fat/date/2024-02-10.json",
            data=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
            json=None,
            params=None,
        )
        assert len(result["fat"]) == 1
        assert result["fat"][0]["logId"] == 1553067000000

    def test_get_weight_logs(self, body_resource, mock_oauth_session, mock_response_factory):
        """Test getting weight logs for a date"""
        mock_response = mock_response_factory(
            200,
            {
                "weight": [
                    {
                        "bmi": 25.91,
                        "date": "2024-02-10",
                        "logId": 1553067494000,
                        "source": "api",
                        "time": "07:38:14",
                        "weight": 200,
                    }
                ]
            },
        )
        mock_oauth_session.request.return_value = mock_response

        result = body_resource.get_weight_logs("2024-02-10")

        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/body/log/weight/date/2024-02-10.json",
            data=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
            json=None,
            params=None,
        )
        assert len(result["weight"]) == 1
        assert result["weight"][0]["logId"] == 1553067494000

    def test_custom_user_id(self, body_resource, mock_oauth_session, mock_response_factory):
        """Test using a custom user ID instead of the default '-'"""
        mock_response = mock_response_factory(200, {"weight": []})
        mock_oauth_session.request.return_value = mock_response

        body_resource.get_weight_logs("2024-02-10", user_id="123ABC")

        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/123ABC/body/log/weight/date/2024-02-10.json",
            data=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
            json=None,
            params=None,
        )

    def test_debug_mode(self, body_resource, capsys):
        """Test debug mode outputs curl command"""
        body_resource.oauth.token = {"access_token": "test-token"}

        result = body_resource.create_weight_log(
            weight=200, date="2024-02-10", time="07:38:14", debug=True
        )

        captured = capsys.readouterr()
        assert result is None
        assert "curl" in captured.out
        assert "POST" in captured.out
        assert "/body/log/weight.json" in captured.out
        assert "weight=200" in captured.out
        assert "date=2024-02-10" in captured.out
        assert "time=07%3A38%3A14" in captured.out

    def test_create_bodyfat_log_validates_date(self, body_resource):
        """Test that create_bodyfat_log validates date format"""
        with raises(InvalidDateException) as exc_info:
            body_resource.create_bodyfat_log(fat=15.0, date="invalid-date")

        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_create_weight_goal_validates_start_date(self, body_resource):
        """Test that create_weight_goal validates start date format"""
        with raises(InvalidDateException) as exc_info:
            body_resource.create_weight_goal(start_date="invalid-date", start_weight=200)

        assert exc_info.value.field_name == "start_date"
        assert "Invalid date format" in str(exc_info.value)

    def test_create_weight_log_validates_date(self, body_resource):
        """Test that create_weight_log validates date format"""
        with raises(InvalidDateException) as exc_info:
            body_resource.create_weight_log(weight=200, date="invalid-date")

        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_bodyfat_log_validates_date(self, body_resource):
        """Test that get_bodyfat_log validates date format"""
        with raises(InvalidDateException) as exc_info:
            body_resource.get_bodyfat_log("invalid-date")

        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)

    def test_get_weight_logs_validates_date(self, body_resource):
        """Test that get_weight_logs validates date format"""
        with raises(InvalidDateException) as exc_info:
            body_resource.get_weight_logs("invalid-date")

        assert exc_info.value.field_name == "date"
        assert "Invalid date format" in str(exc_info.value)
