# tests/resources/test_friends.py

# Standard library imports
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.friends import FriendsResource


class TestFriendsResource:
    @fixture
    def mock_oauth_session(self):
        """Fixture to provide a mock OAuth session"""
        return Mock()

    @fixture
    def mock_response(self):
        """Fixture to provide a mock response"""
        response = Mock()
        response.status_code = 200
        return response

    @fixture
    def mock_logger(self):
        """Fixture to provide a mock logger"""
        return Mock()

    @fixture
    def friends_resource(self, mock_oauth_session, mock_logger):
        """Fixture to provide a FriendsResource instance"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return FriendsResource(
                oauth_session=mock_oauth_session, locale="en_US", language="en_US"
            )

    def test_get_friends(self, friends_resource, mock_oauth_session, mock_response):
        """Test getting friends list"""
        mock_response.json.return_value = {
            "data": [
                {
                    "type": "person",
                    "id": "ABC123",
                    "attributes": {
                        "avatar": "http://example.com/avatar.jpg",
                        "child": False,
                        "friend": True,
                        "name": "Test User",
                    },
                }
            ]
        }
        mock_response.headers = {"content-type": "application/json"}
        mock_oauth_session.request.return_value = mock_response

        result = friends_resource.get_friends()

        assert len(result) == 1
        assert result["data"][0]["type"] == "person"
        assert result["data"][0]["id"] == "ABC123"
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1.1/user/-/friends.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_friends_leaderboard(self, friends_resource, mock_oauth_session, mock_response):
        """Test getting friends leaderboard"""
        mock_response.json.return_value = {
            "data": [
                {
                    "type": "ranked-user",
                    "id": "ABC123",
                    "attributes": {"step-rank": 1, "step-summary": 50000},
                }
            ],
            "included": [
                {
                    "avatar": "http://example.com/avatar.jpg",
                    "child": False,
                    "friend": True,
                    "name": "Test User",
                }
            ],
        }
        mock_response.headers = {"content-type": "application/json"}
        mock_oauth_session.request.return_value = mock_response

        result = friends_resource.get_friends_leaderboard()

        assert "data" in result
        assert "included" in result
        assert len(result["data"]) == 1
        assert result["data"][0]["type"] == "ranked-user"
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1.1/user/-/leaderboard/friends.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )
