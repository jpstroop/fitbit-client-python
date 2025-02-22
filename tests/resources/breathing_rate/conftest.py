# tests/resources/breathing_rate/conftest.py

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.breathing_rate import BreathingRateResource


@fixture()
def breathing_rate_resource(mock_oauth_session, mock_logger):
    """Create a BreathingRateResource with mocked OAuth session"""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return BreathingRateResource(mock_oauth_session, "en_US", "en_US")
