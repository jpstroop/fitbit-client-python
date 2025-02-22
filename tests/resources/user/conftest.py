# tests/resources/user/conftest.py

"""Fixtures for user tests."""

# Standard library imports

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.user import UserResource


@fixture
def user_resource(mock_oauth_session, mock_logger):
    """Create UserResource instance with mocked dependencies"""
    mock_oauth_session.token = {"expires_at": 1234567890}
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return UserResource(mock_oauth_session, "en_US", "en_US")
