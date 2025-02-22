# tests/resources/body/test_delete_weight_log.py

"""Tests for the delete_weight_log endpoint."""


def test_delete_weight_log(body_resource, mock_oauth_session, mock_response_factory):
    """Test deleting a weight log entry"""
    mock_response = mock_response_factory(204)
    mock_oauth_session.request.return_value = mock_response
    result = body_resource.delete_weight_log("1553067494000")
    mock_oauth_session.request.assert_called_once_with(
        "DELETE",
        "https://api.fitbit.com/1/user/-/body/log/weight/1553067494000.json",
        data=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        json=None,
        params=None,
    )
    assert result is None
