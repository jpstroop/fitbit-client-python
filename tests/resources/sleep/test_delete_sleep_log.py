# tests/resources/sleep/test_delete_sleep_log.py

"""Tests for the delete_sleep_log endpoint."""


def test_delete_sleep_log_success(sleep_resource, mock_oauth_session, mock_response_factory):
    """Test successful deletion of sleep log"""
    mock_response = mock_response_factory(204, None)
    mock_oauth_session.request.return_value = mock_response
    result = sleep_resource.delete_sleep_log(log_id="123")
    assert result is None
    mock_oauth_session.request.assert_called_once_with(
        "DELETE",
        "https://api.fitbit.com/1.2/user/-/sleep/123.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
