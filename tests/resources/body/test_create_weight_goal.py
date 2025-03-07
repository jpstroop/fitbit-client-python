# tests/resources/body/test_create_weight_goal.py

"""Tests for the create_weight_goal endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_create_weight_goal_with_weight(body_resource, mock_oauth_session, mock_response_factory):
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
    body_resource, mock_oauth_session, mock_response_factory
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


def test_create_weight_goal_validates_start_date(body_resource):
    """Test that create_weight_goal validates start date format"""
    with raises(InvalidDateException) as exc_info:
        body_resource.create_weight_goal(start_date="invalid-date", start_weight=200)
    assert exc_info.value.field_name == "start_date"
    assert "Invalid date format" in str(exc_info.value)
