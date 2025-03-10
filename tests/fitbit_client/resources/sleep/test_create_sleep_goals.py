# tests/fitbit_client/resources/sleep/test_create_sleep_goals.py

"""Tests for the create_sleep_goals endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import ParameterValidationException


def test_create_sleep_goals_success(sleep_resource, mock_oauth_session, mock_response_factory):
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


def test_create_sleep_goals_invalid_duration(sleep_resource):
    """Test that negative duration raises ParameterValidationException"""
    with raises(ParameterValidationException) as exc_info:
        sleep_resource.create_sleep_goals(min_duration=-1)
    assert "min_duration must be positive" in str(exc_info.value)
    assert exc_info.value.field_name == "min_duration"
