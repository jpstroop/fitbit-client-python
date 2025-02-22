# tests/resources/nutrition/conftest.py

"""Fixtures for nutrition tests."""

# Standard library imports

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.nutrition import NutritionResource


@fixture
def nutrition_resource(mock_oauth_session, mock_logger):
    """Fixture to provide a NutritionResource instance with standard settings"""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        resource = NutritionResource(
            oauth_session=mock_oauth_session, locale="en_US", language="en_US"
        )
        return resource
