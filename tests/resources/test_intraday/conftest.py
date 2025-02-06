# tests/resources/test_intraday/conftest.py

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.intraday import IntradayResource


@fixture
def intraday_resource(mock_oauth_session, mock_logger):
    """Create IntradayResource instance with mocked dependencies"""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return IntradayResource(oauth_session=mock_oauth_session, locale="en_US", language="en_US")
