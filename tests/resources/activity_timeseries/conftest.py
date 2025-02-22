# tests/resources/activity_timeseries/conftest.py

"""Fixtures for activity_timeseries tests."""

# Standard library imports

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.activity_timeseries import ActivityTimeSeriesResource


@fixture
def activity_resource(mock_oauth_session, mock_logger):
    """Fixture to provide an ActivityTimeSeriesResource instance with standard settings"""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        resource = ActivityTimeSeriesResource(
            oauth_session=mock_oauth_session, locale="en_US", language="en_US"
        )
        return resource
