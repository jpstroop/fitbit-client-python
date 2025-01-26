# Third party imports
from pytest import fixture
from requests import Response
from requests_oauthlib import OAuth2Session


@fixture
def mock_oauth_session(mocker):
    """Fixture to provide a mocked OAuth2Session with standard configuration"""
    session = mocker.Mock(spec=OAuth2Session)
    session.request = mocker.Mock()
    return session


@fixture
def mock_response(mocker):
    """Fixture to provide a mocked requests Response with configurable behavior"""
    response = mocker.Mock(spec=Response)
    response.status_code = 200
    response.text = ""
    response.json.return_value = {"success": True}
    response.headers = {}
    response.raise_for_status.return_value = None
    return response
