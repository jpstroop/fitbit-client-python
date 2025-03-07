# tests/resources/sleep/test_get_sleep_goals.py

"""Tests for the get_sleep_goals endpoint."""


def test_get_sleep_goals_success(sleep_resource, mock_oauth_session, mock_response_factory):
    """Test successful retrieval of sleep goals"""
    expected_response = {
        "goal": {"minDuration": 480, "consistency": "ACTIVE", "updatedOn": "2024-02-13"}
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response
    result = sleep_resource.get_sleep_goals()
    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1.2/user/-/sleep/goal.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
