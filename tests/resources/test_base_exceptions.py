# tests/resources/test_base_exceptions.py

# Standard library imports
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import ExpiredTokenException
from fitbit_client.exceptions import FitbitAPIException
from fitbit_client.exceptions import InsufficientPermissionsException
from fitbit_client.exceptions import InsufficientScopeException
from fitbit_client.exceptions import InvalidClientException
from fitbit_client.exceptions import InvalidRequestException
from fitbit_client.exceptions import NotFoundException
from fitbit_client.exceptions import RateLimitExceededException
from fitbit_client.exceptions import SystemException
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.base import BaseResource


class TestBaseResourceExceptions:
    @fixture
    def base_resource(self, mock_oauth_session, mock_logger):
        """Create BaseResource instance with mocked OAuth session"""
        with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
            return BaseResource(mock_oauth_session, "en_US", "en_US")

    def test_400_invalid_request(self, base_resource, mock_oauth_session, mock_response_factory):
        """Test handling of 400 Bad Request with invalid request"""
        mock_response = mock_response_factory(
            400,
            {
                "errors": [
                    {"errorType": "invalid_request", "message": "Missing parameters: refresh_token"}
                ]
            },
        )
        mock_oauth_session.request.return_value = mock_response

        with raises(InvalidRequestException) as exc_info:
            base_resource._make_request("test/endpoint")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "invalid_request"
        assert "Missing parameters: refresh_token" in str(exc_info.value)

    def test_401_expired_token(self, base_resource, mock_oauth_session, mock_response_factory):
        """Test handling of 401 Unauthorized with expired token"""
        mock_response = mock_response_factory(
            401,
            {"errors": [{"errorType": "expired_token", "message": "Access token expired: ABC123"}]},
        )
        mock_oauth_session.request.return_value = mock_response

        with raises(ExpiredTokenException) as exc_info:
            base_resource._make_request("test/endpoint")

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_type == "expired_token"
        assert "Access token expired" in str(exc_info.value)

    def test_401_invalid_client(self, base_resource, mock_oauth_session, mock_response_factory):
        """Test handling of 401 Unauthorized with invalid client"""
        mock_response = mock_response_factory(
            401,
            {
                "errors": [
                    {
                        "errorType": "invalid_client",
                        "message": "Invalid authorization header. Client id invalid",
                    }
                ]
            },
        )
        mock_oauth_session.request.return_value = mock_response

        with raises(InvalidClientException) as exc_info:
            base_resource._make_request("test/endpoint")

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_type == "invalid_client"

    def test_403_insufficient_scope(self, base_resource, mock_oauth_session, mock_response_factory):
        """Test handling of 403 Forbidden with insufficient scope"""
        mock_response = mock_response_factory(
            403,
            {
                "errors": [
                    {
                        "errorType": "insufficient_scope",
                        "message": "This application does not have permission to access sleep data",
                    }
                ]
            },
        )
        mock_oauth_session.request.return_value = mock_response

        with raises(InsufficientScopeException) as exc_info:
            base_resource._make_request("test/endpoint")

        assert exc_info.value.status_code == 403
        assert exc_info.value.error_type == "insufficient_scope"

    def test_403_insufficient_permissions(
        self, base_resource, mock_oauth_session, mock_response_factory
    ):
        """Test handling of 403 Forbidden with insufficient permissions"""
        mock_response = mock_response_factory(
            403,
            {
                "errors": [
                    {
                        "errorType": "insufficient_permissions",
                        "message": "Read-only API client is not authorized to update resources",
                    }
                ]
            },
        )
        mock_oauth_session.request.return_value = mock_response

        with raises(InsufficientPermissionsException) as exc_info:
            base_resource._make_request("test/endpoint")

        assert exc_info.value.status_code == 403
        assert exc_info.value.error_type == "insufficient_permissions"

    def test_404_not_found(self, base_resource, mock_oauth_session, mock_response_factory):
        """Test handling of 404 Not Found"""
        mock_response = mock_response_factory(
            404,
            {
                "errors": [
                    {
                        "errorType": "not_found",
                        "message": "The resource with given id doesn't exist",
                    }
                ]
            },
        )
        mock_oauth_session.request.return_value = mock_response

        with raises(NotFoundException) as exc_info:
            base_resource._make_request("test/endpoint")

        assert exc_info.value.status_code == 404
        assert exc_info.value.error_type == "not_found"

    def test_429_rate_limit(self, base_resource, mock_oauth_session, mock_response_factory):
        """Test handling of 429 Too Many Requests"""
        error_response = {
            "errors": [{"errorType": "rate_limit_exceeded", "message": "Too many requests"}]
        }
        mock_response = mock_response_factory(429, error_response, content_type="application/json")
        mock_oauth_session.request.return_value = mock_response

        with raises(RateLimitExceededException) as exc_info:
            base_resource._make_request("test/endpoint")

        assert exc_info.value.status_code == 429
        assert exc_info.value.error_type == "rate_limit_exceeded"
        assert exc_info.value.raw_response == error_response
        assert "Too many requests" in str(exc_info.value)

    def test_validation_error_with_field(
        self, base_resource, mock_oauth_session, mock_response_factory
    ):
        """Test handling of validation errors that include a field name"""
        mock_response = mock_response_factory(
            400,
            {
                "errors": [
                    {
                        "errorType": "validation",
                        "fieldName": "date",
                        "message": "Invalid date:ABCD-EF-GH",
                    }
                ]
            },
        )
        mock_oauth_session.request.return_value = mock_response

        with raises(ValidationException) as exc_info:
            base_resource._make_request("test/endpoint")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "date"
        assert "Invalid date" in str(exc_info.value)

    def test_make_request_server_error(
        self, base_resource, mock_oauth_session, mock_response_factory
    ):
        """Test handling of 500 server error"""
        mock_response = mock_response_factory(
            500, {"errors": [{"errorType": "system", "message": "Server error"}]}
        )
        mock_oauth_session.request.return_value = mock_response

        with raises(SystemException) as exc_info:
            base_resource._make_request("test/endpoint")

        assert exc_info.value.status_code == 500
        assert exc_info.value.error_type == "system"
        assert "Server error" in str(exc_info.value)

    def test_non_json_error_response(
        self, base_resource, mock_oauth_session, mock_response_factory
    ):
        """Test handling of error responses that aren't valid JSON"""
        mock_response = mock_response_factory(500, content_type="text/plain")
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Internal Server Error"
        mock_oauth_session.request.return_value = mock_response

        with raises(SystemException) as exc_info:
            base_resource._make_request("test/endpoint")

        assert exc_info.value.status_code == 500
        assert exc_info.value.error_type == "system"
        assert "Internal Server Error" in str(exc_info.value)
        expected_response = {
            "errors": [{"errorType": "system", "message": "Internal Server Error"}]
        }
        assert exc_info.value.raw_response == expected_response

    def test_error_with_empty_response(
        self, base_resource, mock_oauth_session, mock_response_factory
    ):
        """Test handling of error responses with no content"""
        mock_response = mock_response_factory(502)
        mock_response.json.return_value = {}
        mock_oauth_session.request.return_value = mock_response

        with raises(FitbitAPIException) as exc_info:
            base_resource._make_request("test/endpoint")

        assert exc_info.value.status_code == 502
