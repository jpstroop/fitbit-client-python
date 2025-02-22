# tests/resources/sleep/conftest.py

"""Fixtures for sleep tests."""

# Standard library imports

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.sleep import SleepResource


@fixture
def sleep_resource(mock_oauth_session, mock_logger):
    """Create SleepResource instance with mocked dependencies"""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return SleepResource(mock_oauth_session, "en_US", "en_US")
