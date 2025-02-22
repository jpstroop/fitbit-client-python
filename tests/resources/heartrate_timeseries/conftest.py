# tests/resources/heartrate_timeseries/conftest.py

"""Fixtures for heartrate_timeseries tests."""

# Standard library imports

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.heartrate_timeseries import HeartrateTimeSeriesResource


@fixture
def heartrate_resource(mock_oauth_session, mock_logger):
    """Fixture to provide a HeartrateTimeSeriesResource instance"""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return HeartrateTimeSeriesResource(
            oauth_session=mock_oauth_session, locale="en_US", language="en_US"
        )
