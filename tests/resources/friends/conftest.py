# tests/resources/friends/conftest.py

"""Fixtures for friends tests."""

# Standard library imports

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.friends import FriendsResource


@fixture
def friends_resource(mock_oauth_session, mock_logger):
    """Fixture to provide a FriendsResource instance"""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return FriendsResource(oauth_session=mock_oauth_session, locale="en_US", language="en_US")
