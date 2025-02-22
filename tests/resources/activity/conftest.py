# tests/resources/activity/conftest.py

"""Fixtures for activity tests."""

# Standard library imports

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.activity import ActivityResource


@fixture
def activity_resource(mock_oauth_session, mock_logger):
    """Create an ActivityResource with mocked OAuth session"""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return ActivityResource(mock_oauth_session, "en_US", "en_US")
