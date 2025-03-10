# tests/fitbit_client/resources/friends/test_get_friends.py

"""Tests for the get_friends endpoint."""


def test_get_friends(friends_resource, mock_oauth_session, mock_response_factory):
    """Test getting friends list"""
    mock_response = mock_response_factory(
        200,
        {
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
        },
    )
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
