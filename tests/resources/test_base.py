# Standard library imports
from json import JSONDecodeError

# Third party imports
import pytest
from requests import HTTPError
from requests import Response

# Local imports
from fitbit_client.resources.base import BaseResource


class TestBaseResource:
    @pytest.fixture
    def base_resource(self, mock_oauth_session):
        """Fixture to provide a BaseResource instance with standard locale settings"""
        return BaseResource(oauth_session=mock_oauth_session, locale="en_US", language="en_US")

    def test_initialization_sets_locale_headers(self, mock_oauth_session):
        """Test initialization properly sets locale-specific headers"""
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

    def test_build_url_empty_endpoint(self, base_resource):
        """Test URL building with empty endpoint"""
        url = base_resource._build_url("")
        assert url == "https://api.fitbit.com/1/user/-/"

    def test_make_request_success(self, base_resource, mock_oauth_session, mock_response):
        """Test successful GET request"""
        mock_response.json.return_value = {"success": True}
        mock_response.headers = {"Content-Type": "application/json"}
        mock_oauth_session.request.return_value = mock_response

        result = base_resource._make_request("test/endpoint")

        assert result["status"] == 200
        assert result["content"]["success"] is True
        assert "Content-Type" in result["headers"]

    def test_make_request_with_params(self, base_resource, mock_oauth_session, mock_response):
        """Test request with query parameters"""
        params = {"date": "2023-01-01"}
        mock_response.headers = {"Content-Type": "application/json"}
        mock_oauth_session.request.return_value = mock_response

        base_resource._make_request("test/endpoint", params=params)

        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/test/endpoint",
            data=None,
            json=None,
            params=params,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

    def test_make_request_delete(self, base_resource, mock_oauth_session, mock_response):
        """Test DELETE request handling"""
        mock_response.status_code = 204
        mock_response.text = ""
        mock_response.headers = {}
        mock_oauth_session.request.return_value = mock_response

        result = base_resource._make_request("test/endpoint", http_method="DELETE")

        assert result["status"] == 204
        assert result["content"] == ""
        assert isinstance(result["headers"], dict)

    def test_make_request_server_error(self, base_resource, mock_oauth_session, mock_response):
        """Test server error (500) handling"""
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = HTTPError("Server Error")
        mock_oauth_session.request.return_value = mock_response

        with pytest.raises(HTTPError):
            base_resource._make_request("test/endpoint")

    def test_make_request_client_error(self, base_resource, mock_oauth_session, mock_response):
        """Test client error (400) handling"""
        mock_response.status_code = 400
        mock_response.json.return_value = {"errors": [{"message": "Bad Request"}]}
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.raise_for_status.side_effect = HTTPError("Client Error")
        mock_oauth_session.request.return_value = mock_response

        result = base_resource._make_request("test/endpoint")

        assert result["status"] == 400
        assert "errors" in result["content"]

    def test_make_request_json_decode_error(self, base_resource, mock_oauth_session, mock_response):
        """Test JSON decode error handling with full context"""
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "doc", 0)
        mock_response.text = "Invalid {json"
        mock_response.headers = {"Content-Type": "application/json", "X-Request-Id": "123"}
        mock_oauth_session.request.return_value = mock_response

        with pytest.raises(JSONDecodeError) as exc_info:
            base_resource._make_request("test/endpoint")

        # Verify the error includes additional context
        error_str = str(exc_info.value)
        assert hasattr(exc_info.value, "__notes__")

        # The exact implementation of notes may vary by Python version,
        # but we can verify the error contains our added context
        full_error = str(exc_info.value) + str(getattr(exc_info.value, "__notes__", ""))
