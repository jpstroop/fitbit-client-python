# Third party imports
from pytest import fixture
from requests_oauthlib import OAuth2Session


@fixture
def mock_oauth_session(mocker):
    """Fixture to provide a mocked OAuth2Session"""
    session = mocker.Mock(spec=OAuth2Session)
    return session


@fixture
def mock_response(mocker):
    """Fixture to provide a mocked requests Response object"""
    response = mocker.Mock()
    response.status_code = 200
    response.json.return_value = {"success": True}
    response.headers = {}
    return response
