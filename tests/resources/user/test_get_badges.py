# tests/resources/user/test_get_badges.py

"""Tests for the get_badges endpoint."""


def test_get_badges_success(user_resource, mock_oauth_session, mock_response_factory):
    """Test successful retrieval of badges"""
    expected_response = {
        "badges": [
            {
                "badgeGradientEndColor": "123456",
                "badgeGradientStartColor": "123456",
                "badgeType": "DAILY_STEPS",
                "category": "Daily Steps",
                "cheers": [],
                "dateTime": "2024-02-13",
                "description": "10,000 steps in a day",
                "earnedMessage": "Congratulations! You've earned the Sneakers badge!",
                "encodedId": "123456789",
                "image100px": "https://image.url",
                "image125px": "https://image.url",
                "image300px": "https://image.url",
                "image50px": "https://image.url",
                "image75px": "https://image.url",
                "marketingDescription": (
                    "You've walked 10,000 steps! Congrats on earning the sneaker badge."
                ),
                "mobileDescription": "You've walked 10,000 steps!",
                "name": "Sneakers",
                "shareImage640px": "https://image.url",
                "shareText": "I took 10,000 steps today and earned the Sneakers badge! #Fitbit",
                "shortDescription": "10,000 steps",
                "shortName": "Sneakers",
                "timesAchieved": 1,
                "unit": "STEPS",
                "value": 10000,
            }
        ]
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response
    result = user_resource.get_badges()
    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/badges.json",
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
