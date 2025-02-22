# tests/resources/spo2/conftest.py

"""Fixtures for spo2 tests."""

# Standard library imports

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.spo2 import SpO2Resource


@fixture
def spo2_resource(mock_oauth_session, mock_logger):
    """Create SpO2Resource instance with mocked dependencies"""
    mock_oauth_session.token = {"expires_at": 1234567890}
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return SpO2Resource(mock_oauth_session, "en_US", "en_US")
