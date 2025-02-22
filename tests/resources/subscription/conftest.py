# tests/resources/subscription/conftest.py

"""Fixtures for subscription tests."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.subscription import SubscriptionResource


@fixture
def subscription_resource(mock_oauth_session, mock_logger):
    """Create a SubscriptionResource with mocked OAuth session"""
    mock_oauth_session.token = {"expires_at": 1234567890}
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return SubscriptionResource(mock_oauth_session, "en_US", "en_US")
