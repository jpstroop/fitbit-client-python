# tests/resources/irregular_rhythm_notifications/conftest.py

"""Fixtures for irregular_rhythm_notifications tests."""

# Standard library imports

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.irregular_rhythm_notifications import (
    IrregularRhythmNotificationsResource,
)


@fixture
def irn_resource(mock_oauth_session, mock_logger):
    """Create IrregularRhythmNotificationsResource instance with mocked dependencies"""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return IrregularRhythmNotificationsResource(mock_oauth_session, "en_US", "en_US")
