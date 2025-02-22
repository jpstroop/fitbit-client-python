# tests/resources/body/conftest.py

"""Fixtures for body tests."""

# Standard library imports

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.body import BodyResource


@fixture
def body_resource(mock_oauth_session, mock_logger):
    """Create BodyResource instance with mocked OAuth session"""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return BodyResource(mock_oauth_session, "en_US", "en_US")
