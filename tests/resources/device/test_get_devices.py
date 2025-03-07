# tests/resources/device/test_get_devices.py

"""Tests for the get_devices endpoint."""

# Third party imports

# Third party imports
from pytest import mark
from pytest import raises


def test_get_devices_success(device_resource, mock_oauth_session, mock_response_factory):
    """Test successful retrieval of devices list."""
    mock_response = mock_response_factory(
        200,
        [
            {
                "battery": "Medium",
                "batteryLevel": 60,
                "deviceVersion": "Charge 2",
                "features": [],
                "id": "816713257",
                "lastSyncTime": "2019-11-07T12:00:58.000",
                "mac": "16ADD56D54GD",
                "type": "TRACKER",
            }
        ],
    )
    mock_oauth_session.request.return_value = mock_response
    result = device_resource.get_devices()
    assert isinstance(result, list)
    assert len(result) == 1
    device = result[0]
    assert device["id"] == "816713257"
    assert device["deviceVersion"] == "Charge 2"
    assert device["battery"] == "Medium"
    assert device["batteryLevel"] == 60
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/devices.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_devices_debug_mode(device_resource, mock_oauth_session, capsys):
    """Test get_devices in debug mode prints curl command and returns None."""
    mock_oauth_session.token = {"access_token": "test_token"}
    result = device_resource.get_devices(debug=True)
    mock_oauth_session.request.assert_not_called()
    captured = capsys.readouterr()
    assert "curl" in captured.out
    assert "devices.json" in captured.out
    assert "Authorization: Bearer test_token" in captured.out
    assert result is None


@mark.parametrize("status_code", [400, 401, 403, 404, 429, 500])
def test_get_devices_error_responses(
    device_resource, mock_oauth_session, mock_response_factory, status_code
):
    """Test handling of various error responses."""
    mock_response = mock_response_factory(
        status_code, {"errors": [{"errorType": "system", "message": f"Error {status_code}"}]}
    )
    mock_oauth_session.request.return_value = mock_response
    with raises(Exception) as exc_info:
        device_resource.get_devices()
    assert exc_info.value.status_code == status_code
