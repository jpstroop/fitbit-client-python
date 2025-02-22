# tests/resources/nutrition_timeseries/conftest.py

"""Fixtures for nutrition_timeseries tests."""

# Standard library imports

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.nutrition_timeseries import NutritionTimeSeriesResource


@fixture
def nutrition_timeseries_resource(mock_oauth_session, mock_logger):
    """Create NutritionTimeSeriesResource instance"""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return NutritionTimeSeriesResource(mock_oauth_session, "en_US", "en_US")
