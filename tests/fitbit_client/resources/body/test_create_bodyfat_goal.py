# tests/fitbit_client/resources/body/test_create_bodyfat_goal.py

"""Tests for the create_bodyfat_goal endpoint."""


def test_create_bodyfat_goal(body_resource, mock_oauth_session, mock_response_factory):
    """Test creating a body fat goal"""
    mock_response = mock_response_factory(201, {"goal": {"fat": 25}})
    mock_oauth_session.request.return_value = mock_response
    result = body_resource.create_bodyfat_goal(fat=25.0)
    mock_oauth_session.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/body/log/fat/goal.json",
        data=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        json=None,
        params={"fat": 25.0},
    )
    assert result["goal"]["fat"] == 25
