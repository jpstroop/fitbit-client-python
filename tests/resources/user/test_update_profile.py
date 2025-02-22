# tests/resources/user/test_update_profile.py

"""Tests for the update_profile endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.resources.constants import ClockTimeFormat
from fitbit_client.resources.constants import Gender
from fitbit_client.resources.constants import StartDayOfWeek


def test_update_profile_success(user_resource, mock_oauth_session, mock_response_factory):
    """Test successful update of user profile"""
    expected_response = {
        "user": {"fullName": "Updated User", "gender": "MALE", "birthday": "1990-01-01"}
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response
    result = user_resource.update_profile(
        gender=Gender.MALE, birthday="1990-01-01", full_name="Updated User"
    )
    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/profile.json",
        data=None,
        json=None,
        params={"gender": "MALE", "birthday": "1990-01-01", "fullName": "Updated User"},
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_update_profile_with_all_fields(user_resource, mock_oauth_session, mock_response_factory):
    """Test update with all possible fields"""
    mock_response = mock_response_factory(200, {"user": {}})
    mock_oauth_session.request.return_value = mock_response
    result = user_resource.update_profile(
        gender=Gender.MALE,
        birthday="1990-01-01",
        height="1.75",
        about_me="About me text",
        full_name="Full Name",
        country="US",
        state="CA",
        city="San Francisco",
        clock_time_display_format=ClockTimeFormat.TWELVE_HOUR,
        start_day_of_week=StartDayOfWeek.MONDAY,
        locale="en_US",
        locale_lang="en",
        locale_country="US",
        timezone="America/Los_Angeles",
        foods_locale="en_US",
        glucose_unit="en_US",
        height_unit="en_US",
        water_unit="ml",
        weight_unit="kg",
        stride_length_walking="0.5",
        stride_length_running="0.7",
    )
    mock_oauth_session.request.assert_called_once()
    called_params = mock_oauth_session.request.call_args[1]["params"]
    assert called_params["gender"] == "MALE"
    assert called_params["birthday"] == "1990-01-01"
    assert called_params["height"] == "1.75"
    assert called_params["aboutMe"] == "About me text"
    assert called_params["fullName"] == "Full Name"
    assert called_params["country"] == "US"
    assert called_params["state"] == "CA"
    assert called_params["city"] == "San Francisco"
    assert called_params["clockTimeDisplayFormat"] == "12hour"
    assert called_params["startDayOfWeek"] == "MONDAY"
    assert called_params["locale"] == "en_US"
    assert called_params["localeLang"] == "en"
    assert called_params["localeCountry"] == "US"
    assert called_params["timezone"] == "America/Los_Angeles"
    assert called_params["foodsLocale"] == "en_US"
    assert called_params["glucoseUnit"] == "en_US"
    assert called_params["heightUnit"] == "en_US"
    assert called_params["waterUnit"] == "ml"
    assert called_params["weightUnit"] == "kg"
    assert called_params["strideLengthWalking"] == "0.5"
    assert called_params["strideLengthRunning"] == "0.7"


def test_update_profile_with_only_birthday(
    user_resource, mock_oauth_session, mock_response_factory
):
    """Test update with only birthday field"""
    mock_response = mock_response_factory(200, {"user": {}})
    mock_oauth_session.request.return_value = mock_response
    result = user_resource.update_profile(birthday="1990-01-01")
    mock_oauth_session.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/profile.json",
        data=None,
        json=None,
        params={"birthday": "1990-01-01"},
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_update_profile_invalid_birthday(user_resource, mock_oauth_session):
    """Test that invalid birthday format raises InvalidDateException"""
    with raises(InvalidDateException):
        user_resource.update_profile(birthday="invalid-date")


def test_update_profile_allows_none_values(
    user_resource, mock_oauth_session, mock_response_factory
):
    """Test that None values are handled correctly"""
    mock_response = mock_response_factory(200, {"user": {}})
    mock_oauth_session.request.return_value = mock_response
    result = user_resource.update_profile(gender=None, birthday=None, full_name="Updated User")
    mock_oauth_session.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/profile.json",
        data=None,
        json=None,
        params={"fullName": "Updated User"},
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_update_profile_birthday_allows_today(
    user_resource, mock_oauth_session, mock_response_factory
):
    """Test that 'today' is accepted as birthday value (while not typical, it's valid date format)"""
    mock_response = mock_response_factory(200, {"user": {}})
    mock_oauth_session.request.return_value = mock_response
    user_resource.update_profile(birthday="today")


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
