# tests/client/test_client.py

# Standard library imports
from unittest.mock import MagicMock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.client.fitbit_client import FitbitClient


@fixture
def mock_oauth():
    with patch("fitbit_client.client.fitbit_client.FitbitOAuth2") as mock:
        mock_auth = MagicMock()
        mock.return_value = mock_auth
        yield mock_auth


@fixture
def client(mock_oauth):
    return FitbitClient(
        client_id="test_id", client_secret="test_secret", redirect_uri="https://localhost:8080"
    )


# def test_client_init(client):
#     """Test client initialization creates all resource instances"""
#     assert hasattr(client, 'auth')
#     assert hasattr(client, 'active_zone')
#     assert hasattr(client, 'activity')
#     assert hasattr(client, 'sleep')
#     assert hasattr(client, 'user')


def test_client_authenticate(client, mock_oauth):
    """Test client authentication delegates to OAuth handler"""
    mock_oauth.authenticate.return_value = True
    assert client.authenticate() is True
    mock_oauth.authenticate.assert_called_once_with(force_new=False)


def test_client_authenticate_force_new(client, mock_oauth):
    """Test forced new authentication"""
    mock_oauth.authenticate.return_value = True
    assert client.authenticate(force_new=True) is True
    mock_oauth.authenticate.assert_called_once_with(force_new=True)


def test_client_authenticate_error(client, mock_oauth):
    """Test authentication error handling"""
    mock_oauth.authenticate.side_effect = RuntimeError("Auth failed")
    with raises(RuntimeError):
        client.authenticate()
