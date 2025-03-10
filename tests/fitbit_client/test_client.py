# tests/fitbit_client/test_client.py

# Standard library imports
from unittest.mock import MagicMock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.client import FitbitClient
from fitbit_client.exceptions import OAuthException
from fitbit_client.exceptions import SystemException


@fixture
def mock_oauth():
    with patch("fitbit_client.client.FitbitOAuth2") as mock:
        mock_auth = MagicMock()
        mock.return_value = mock_auth
        yield mock_auth


@fixture
def client(mock_oauth):  # We have to pass the mock even though it does not appear
    # to be used; otherwise the actual auth flow will start!
    return FitbitClient(
        client_id="test_id", client_secret="test_secret", redirect_uri="https://localhost:8080"
    )


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


def test_client_authenticate_oauth_error(client, mock_oauth):
    """Test OAuth authentication error handling"""
    mock_error = OAuthException(message="Auth failed", error_type="oauth", status_code=400)
    mock_oauth.authenticate.side_effect = mock_error
    with raises(OAuthException) as exc_info:
        client.authenticate()
    assert "Auth failed" in str(exc_info.value)


def test_client_authenticate_system_error(client, mock_oauth):
    """Test system error handling"""
    mock_error = SystemException(message="System failure", error_type="system", status_code=500)
    mock_oauth.authenticate.side_effect = mock_error
    with raises(SystemException) as exc_info:
        client.authenticate()
    assert "System failure" in str(exc_info.value)


def test_client_rate_limiting_config():
    """Test that client passes rate limiting config to resources"""
    with (
        patch("fitbit_client.client.FitbitOAuth2") as mock_oauth2,
        patch("fitbit_client.client.SleepResource") as mock_sleep_resource,
    ):

        # Set up mocks
        mock_auth = MagicMock()
        mock_auth.session = "mock_session"
        mock_oauth2.return_value = mock_auth

        # Create client with custom rate limiting config
        client = FitbitClient(
            client_id="test_id",
            client_secret="test_secret",
            redirect_uri="http://localhost:8080/callback",
            max_retries=5,
            retry_after_seconds=30,
            retry_backoff_factor=2.0,
        )

        # Verify rate limiting params were passed to SleepResource
        assert mock_sleep_resource.call_args is not None
        args, kwargs = mock_sleep_resource.call_args
        assert kwargs["max_retries"] == 5
        assert kwargs["retry_after_seconds"] == 30
        assert kwargs["retry_backoff_factor"] == 2.0
