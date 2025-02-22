# tests/resources/cardio_fitness_score/conftest.py

"""Fixtures for cardio_fitness_score tests."""

# Standard library imports

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.cardio_fitness_score import CardioFitnessScoreResource


@fixture
def cardio_fitness_score_resource(mock_oauth_session, mock_logger):
    """Create a CardioFitnessResource with mocked OAuth session"""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return CardioFitnessScoreResource(mock_oauth_session, "en_US", "en_US")
