# tests/resources/test_base.py

# Standard library imports
from json import JSONDecodeError
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises
from requests import Response

# Local imports
from fitbit_client.resources.base import BaseResource


class TestBaseResource:
    @fixture
    def mock_logger(self):
        """Fixture to provide a mock logger"""
        return Mock()

    @fixture
    def base_resource(self, mock_oauth_session, mock_logger):
        """Fixture to provide a BaseResource instance with standard locale settings"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            resource = BaseResource(
                oauth_session=mock_oauth_session, locale="en_US", language="en_US"
            )
            return resource

    def test_initialization_sets_locale_headers(self, mock_oauth_session):
        """Test initialization properly sets locale-specific headers"""
        with patch("fitbit_client.resources.base.getLogger"):
            resource = BaseResource(mock_oauth_session, "fr_FR", "fr")
            assert resource.headers == {"Accept-Locale": "fr_FR", "Accept-Language": "fr"}
            assert resource.oauth == mock_oauth_session

    def test_build_url_with_user_endpoint(self, base_resource):
        """Test URL building with user endpoint"""
        url = base_resource._build_url("test/endpoint", user_id="123")
        assert url == "https://api.fitbit.com/1/user/123/test/endpoint"

    def test_build_url_with_public_endpoint(self, base_resource):
        """Test URL building with public endpoint"""
        url = base_resource._build_url("foods/units", requires_user_id=False)
        assert url == "https://api.fitbit.com/1/foods/units"

    def test_build_url_with_version(self, base_resource):
        """Test URL building with specific API version"""
        url = base_resource._build_url("friends", api_version="1.1")
        assert url == "https://api.fitbit.com/1.1/user/-/friends"

    def test_get_calling_method(self, base_resource):
        """Test getting the calling method name skips internal methods"""

        def wrapper_method():
            def _make_request():
                return base_resource._get_calling_method()

            return _make_request()

        method_name = wrapper_method()
        assert method_name == "wrapper_method"

    @patch("fitbit_client.resources.base.currentframe")
    def test_get_calling_method_with_frames(self, mock_frame, base_resource):
        """Test getting the calling method name with specific frame setup"""
        # Set up the frame chain:
        # api_method -> _make_request -> _get_calling_method

        api_frame = Mock()
        api_frame.f_code.co_name = "api_method"
        api_frame.f_back = None

        make_request_frame = Mock()
        make_request_frame.f_code.co_name = "_make_request"
        make_request_frame.f_back = api_frame

        get_calling_frame = Mock()
        get_calling_frame.f_code.co_name = "_get_calling_method"
        get_calling_frame.f_back = make_request_frame

        mock_frame.return_value = get_calling_frame

        result = base_resource._get_calling_method()
        assert result == "api_method"

    def test_log_response_error_with_field(self, base_resource, mock_logger):
        """Test error logging with field name"""
        response = Response()
        response.status_code = 400
        content = {
            "errors": [
                {"errorType": "validation", "fieldName": "date", "message": "Invalid date format"}
            ]
        }

        base_resource._log_response("test_method", "test/endpoint", response, content)
        mock_logger.error.assert_called_with(
            "Request failed for test/endpoint "
            "(method: test_method, status: 400): "
            "[validation] date: Invalid date format"
        )

    def test_log_response_error_without_field(self, base_resource, mock_logger):
        """Test error logging without field name"""
        response = Response()
        response.status_code = 400
        content = {"errors": [{"errorType": "system", "message": "Service unavailable"}]}

        base_resource._log_response("test_method", "test/endpoint", response, content)
        mock_logger.error.assert_called_with(
            "Request failed for test/endpoint "
            "(method: test_method, status: 400): "
            "[system] Service unavailable"
        )

    def test_log_response_success(self, base_resource, mock_logger):
        """Test success logging"""
        response = Response()
        response.status_code = 200

        base_resource._log_response("test_method", "test/endpoint", response)
        mock_logger.info.assert_called_with("test_method succeeded for test/endpoint (status 200)")

    def test_handle_json_response(self, base_resource, mock_response):
        """Test JSON response handling"""
        mock_response.json.return_value = {"data": "test"}
        mock_response.status_code = 200

        result = base_resource._handle_json_response("test_method", "test/endpoint", mock_response)
        assert result == {"data": "test"}

    def test_handle_json_response_invalid(self, base_resource, mock_response):
        """Test invalid JSON handling"""
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "doc", 0)
        mock_response.text = "Invalid {json"

        with raises(JSONDecodeError):
            base_resource._handle_json_response("test_method", "test/endpoint", mock_response)

    def test_make_request_json_success(self, base_resource, mock_oauth_session, mock_response):
        """Test successful JSON request"""
        mock_response.json.return_value = {"success": True}
        mock_response.headers = {"content-type": "application/json"}
        mock_response.status_code = 200
        mock_oauth_session.request.return_value = mock_response

        result = base_resource._make_request("test/endpoint")
        assert result == {"success": True}

    def test_make_request_no_content(self, base_resource, mock_oauth_session, mock_response):
        """Test request with no content"""
        mock_response.status_code = 204
        mock_response.headers = {}
        mock_oauth_session.request.return_value = mock_response

        result = base_resource._make_request("test/endpoint")
        assert result is None

    def test_make_request_xml_response(self, base_resource, mock_oauth_session, mock_response):
        """Test XML response handling"""
        mock_response.text = "<test>data</test>"
        mock_response.headers = {"content-type": "application/vnd.garmin.tcx+xml"}
        mock_response.status_code = 200
        mock_oauth_session.request.return_value = mock_response

        result = base_resource._make_request("test/endpoint")
        assert result == "<test>data</test>"

    def test_make_request_unexpected_content_type(
        self, base_resource, mock_oauth_session, mock_response
    ):
        """Test handling of unexpected content type"""
        mock_response.text = "some data"
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.status_code = 200
        mock_oauth_session.request.return_value = mock_response

        result = base_resource._make_request("test/endpoint")
        assert result == "some data"
