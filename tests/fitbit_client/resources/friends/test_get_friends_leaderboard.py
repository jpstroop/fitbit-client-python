# tests/fitbit_client/resources/friends/test_get_friends_leaderboard.py

"""Tests for the get_friends_leaderboard endpoint."""


def test_get_friends_leaderboard(friends_resource, mock_oauth_session, mock_response_factory):
    """Test getting friends leaderboard"""
    mock_response = mock_response_factory(
        200,
        {
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
        },
    )
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
