# tests/fitbit_client/resources/user/test_get_profile.py

"""Tests for the get_profile endpoint."""


def test_get_profile_success(user_resource, mock_oauth_session, mock_response_factory):
    """Test successful retrieval of user profile"""
    expected_response = {
        "user": {"fullName": "Test User", "gender": "MALE", "birthday": "1990-01-01"}
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response
    result = user_resource.get_profile()
    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/profile.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_custom_user_id(user_resource, mock_oauth_session, mock_response_factory):
    """Test endpoints with custom user ID"""
    custom_user_id = "123ABC"
    mock_response = mock_response_factory(200, {"user": {}})
    mock_oauth_session.request.return_value = mock_response
    user_resource.get_profile(user_id=custom_user_id)
    mock_oauth_session.request.assert_called_with(
        "GET",
        f"https://api.fitbit.com/1/user/{custom_user_id}/profile.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
    user_resource.update_profile(birthday="1990-01-01", user_id=custom_user_id)
    mock_oauth_session.request.assert_called_with(
        "POST",
        f"https://api.fitbit.com/1/user/{custom_user_id}/profile.json",
        data=None,
        json=None,
        params={"birthday": "1990-01-01"},
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
    user_resource.get_badges(user_id=custom_user_id)
    mock_oauth_session.request.assert_called_with(
        "GET",
        f"https://api.fitbit.com/1/user/{custom_user_id}/badges.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
