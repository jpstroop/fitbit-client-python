# tests/resources/test_device.py

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import mark
from pytest import raises

# Local imports
from fitbit_client.resources.device import DeviceResource


class TestDeviceResource:
    """Test suite for the DeviceResource class."""

    @fixture
    def device_resource(self, mock_oauth_session, mock_logger):
        """Create DeviceResource instance with mocked dependencies."""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return DeviceResource(mock_oauth_session, "en_US", "en_US")

    def test_get_devices_success(self, device_resource, mock_oauth_session, mock_response_factory):
        """Test successful retrieval of devices list."""
        # Setup mock response with example device data
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

        # Call method and verify response
        result = device_resource.get_devices()

        assert isinstance(result, list)
        assert len(result) == 1
        device = result[0]
        assert device["id"] == "816713257"
        assert device["deviceVersion"] == "Charge 2"
        assert device["battery"] == "Medium"
        assert device["batteryLevel"] == 60

        # Verify correct API call was made
        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/devices.json",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_get_devices_debug_mode(self, device_resource, mock_oauth_session, capsys):
        """Test get_devices in debug mode prints curl command and returns None."""
        # Mock the OAuth token
        mock_oauth_session.token = {"access_token": "test_token"}

        result = device_resource.get_devices(debug=True)

        # Verify no API call was made
        mock_oauth_session.request.assert_not_called()

        # Verify curl command was printed
        captured = capsys.readouterr()
        assert "curl" in captured.out
        assert "devices.json" in captured.out
        assert "Authorization: Bearer test_token" in captured.out
        assert result is None

    @mark.parametrize("status_code", [400, 401, 403, 404, 429, 500])
    def test_get_devices_error_responses(
        self, device_resource, mock_oauth_session, mock_response_factory, status_code
    ):
        """Test handling of various error responses."""
        mock_response = mock_response_factory(
            status_code, {"errors": [{"errorType": "system", "message": f"Error {status_code}"}]}
        )
        mock_oauth_session.request.return_value = mock_response

        with raises(Exception) as exc_info:
            device_resource.get_devices()

        assert exc_info.value.status_code == status_code

    def test_create_alarm_not_implemented(self, device_resource):
        """Test create_alarm raises NotImplementedError."""
        with raises(NotImplementedError):
            device_resource.create_alarm(
                tracker_id="123",
                time="07:00-08:00",
                enabled=True,
                recurring=True,
                week_days=["MONDAY"],
            )

    def test_delete_alarm_not_implemented(self, device_resource):
        """Test delete_alarm raises NotImplementedError."""
        with raises(NotImplementedError):
            device_resource.delete_alarm(tracker_id="123", alarm_id="456")

    def test_get_alarms_not_implemented(self, device_resource):
        """Test get_alarms raises NotImplementedError."""
        with raises(NotImplementedError):
            device_resource.get_alarms(tracker_id="123")

    def test_update_alarm_not_implemented(self, device_resource):
        """Test update_alarm raises NotImplementedError."""
        with raises(NotImplementedError):
            device_resource.update_alarm(
                tracker_id="123",
                alarm_id="456",
                time="07:00-08:00",
                enabled=True,
                recurring=True,
                week_days=["MONDAY"],
                snooze_length=5,
                snooze_count=3,
            )
