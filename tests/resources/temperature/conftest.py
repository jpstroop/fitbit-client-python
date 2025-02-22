# tests/resources/temperature/conftest.py

"""Fixtures for temperature tests."""

# Standard library imports

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.temperature import TemperatureResource


@fixture
def temperature_resource(mock_oauth_session, mock_logger):
    """Create TemperatureResource instance with mocked dependencies"""
    mock_oauth_session.token = {"expires_at": 1234567890}
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return TemperatureResource(mock_oauth_session, "en_US", "en_US")
