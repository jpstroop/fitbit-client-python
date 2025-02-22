# tests/resources/active_zone_minutes/conftest.py

"""Fixtures for active_zone_minutes tests."""

# Standard library imports

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.active_zone_minutes import ActiveZoneMinutesResource


@fixture
def azm_resource(mock_oauth_session, mock_logger):
    """Fixture to provide an ActiveZoneMinutesResource instance"""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return ActiveZoneMinutesResource(
            oauth_session=mock_oauth_session, locale="en_US", language="en_US"
        )
