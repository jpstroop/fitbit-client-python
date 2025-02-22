# tests/resources/electrocardiogram/conftest.py

"""Fixtures for electrocardiogram tests."""

# Standard library imports

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.electrocardiogram import ElectrocardiogramResource


@fixture
def ecg_resource(mock_oauth_session, mock_logger):
    """Create ElectrocardiogramResource instance with mocked dependencies"""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return ElectrocardiogramResource(mock_oauth_session, "en_US", "en_US")
