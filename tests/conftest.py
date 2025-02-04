# tests/conftest.py

# Standard library imports
from unittest.mock import Mock

# Third party imports
from pytest import fixture
from requests import Response
from requests_oauthlib import OAuth2Session


@fixture
def mock_oauth_session():
    """Fixture to provide a mocked OAuth2Session with standard configuration"""
    session = Mock(spec=OAuth2Session)
    session.request = Mock()
    return session


@fixture
def mock_response():
    """Fixture to provide a mocked requests Response with configurable behavior"""
    response = Mock(spec=Response)
    response.status_code = 200
    response.text = ""
    response.json.return_value = {"success": True}
    response.headers = {"content-type": "application/json"}
    response.raise_for_status.return_value = None
    return response


@fixture
def mock_server():
    """Provide a mock server instance"""
    server = Mock()
    server.last_callback = None
    return server


@fixture
def mock_logger():
    """Fixture to provide a mock logger that's used across resources"""
    return Mock()


@fixture
def mock_response_factory():
    """Factory fixture for creating mock responses with specific attributes"""

    def _create_mock_response(status_code, json_data=None, content_type="application/json"):
        response = Mock(spec=Response)
        response.status_code = status_code
        response.headers = {"content-type": content_type}
        response.text = ""  # Default empty text
        if json_data:
            response.json.return_value = json_data
        else:
            response.json.return_value = {}
        return response

    return _create_mock_response
