# tests/resources/device/conftest.py

"""Fixtures for device tests."""

# Standard library imports

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.device import DeviceResource


@fixture
def device_resource(mock_oauth_session, mock_logger):
    """Create DeviceResource instance with mocked dependencies."""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return DeviceResource(mock_oauth_session, "en_US", "en_US")
