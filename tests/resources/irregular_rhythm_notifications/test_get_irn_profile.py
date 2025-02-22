# tests/resources/irregular_rhythm_notifications/test_get_irn_profile.py

"""Tests for the get_irn_profile endpoint."""


def test_get_irn_profile_success(irn_resource, mock_oauth_session, mock_response_factory):
    """Test successful retrieval of IRN profile"""
    expected_response = {
        "onboarded": True,
        "enrolled": True,
        "lastUpdated": "2022-09-28T17:12:30.000",
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response
    result = irn_resource.get_irn_profile()
    assert result == expected_response
    mock_oauth_session.request.assert_called_once()
    call_args = mock_oauth_session.request.call_args
    assert call_args[0][0] == "GET"
    assert call_args[0][1].endswith("/1/user/-/irn/profile.json")


def test_debug_mode(irn_resource, mock_oauth_session, capsys):
    """Test that debug mode prints curl command and returns None"""
    mock_oauth_session.token = {"access_token": "test-token-123"}
    result = irn_resource.get_irn_profile(debug=True)
    captured = capsys.readouterr()
    assert result is None
    assert "curl" in captured.out
    assert "irn/profile.json" in captured.out
    assert "Bearer test-token-123" in captured.out


def test_get_irn_profile_custom_user_id(irn_resource, mock_oauth_session, mock_response_factory):
    """Test IRN profile retrieval with custom user ID"""
    mock_response = mock_response_factory(200, {"onboarded": True})
    mock_oauth_session.request.return_value = mock_response
    irn_resource.get_irn_profile(user_id="123ABC")
    call_args = mock_oauth_session.request.call_args
    assert "user/123ABC/irn/profile.json" in call_args[0][1]
