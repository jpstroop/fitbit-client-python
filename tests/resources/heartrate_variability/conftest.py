# tests/resources/heartrate_variability/conftest.py

"""Fixtures for heartrate_variability tests."""

# Standard library imports

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.heartrate_variability import HeartrateVariabilityResource


@fixture
def hrv_resource(mock_oauth_session, mock_logger):
    """Create HeartrateVariabilityResource instance with mocked dependencies"""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return HeartrateVariabilityResource(mock_oauth_session, "en_US", "en_US")
