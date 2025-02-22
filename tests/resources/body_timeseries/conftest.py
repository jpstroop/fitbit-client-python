# tests/resources/body_timeseries/conftest.py

"""Fixtures for body_timeseries tests."""

# Standard library imports

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.body_timeseries import BodyTimeSeriesResource


@fixture
def body_timeseries(mock_oauth_session, mock_logger):
    """Create BodyTimeSeriesResource instance"""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return BodyTimeSeriesResource(mock_oauth_session, "en_US", "en_US")
