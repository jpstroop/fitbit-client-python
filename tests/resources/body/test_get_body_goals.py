# tests/resources/body/test_get_body_goals.py

"""Tests for the get_body_goals endpoint."""

# Local imports

# Local imports
from fitbit_client.resources.constants import BodyGoalType


def test_get_body_goals_fat(body_resource, mock_oauth_session, mock_response_factory):
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


def test_get_body_goals_weight(body_resource, mock_oauth_session, mock_response_factory):
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
