# tests/resources/test_base.py

"""Tests for BaseResource"""

# This file is looong. Sorry. Almost all of the behavior of the resource
# methods is covered here. The tests of the individual resource methods
# are really just focused on different parameter combinations, validations, and
# more specific exceptions.


# Standard library imports
from json import JSONDecodeError
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import raises
from requests import Response

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

# -----------------------------------------------------------------------------
# 1. Initialization and Basic Setup
# -----------------------------------------------------------------------------


def test_initialization_sets_locale_headers(mock_oauth_session):
    """Test initialization properly sets locale-specific headers"""
    with patch("fitbit_client.resources.base.getLogger"):
        resource = BaseResource(mock_oauth_session, "fr_FR", "fr")
        assert resource.headers == {"Accept-Locale": "fr_FR", "Accept-Language": "fr"}
        assert resource.oauth == mock_oauth_session


# -----------------------------------------------------------------------------
# 2. URL Building
# -----------------------------------------------------------------------------


def test_build_url_with_user_endpoint(base_resource):
    """Test URL building with user endpoint"""
    url = base_resource._build_url("test/endpoint", user_id="123")
    assert url == "https://api.fitbit.com/1/user/123/test/endpoint"


def test_build_url_with_public_endpoint(base_resource):
    """Test URL building with public endpoint"""
    url = base_resource._build_url("foods/units", requires_user_id=False)
    assert url == "https://api.fitbit.com/1/foods/units"


def test_build_url_with_version(base_resource):
    """Test URL building with specific API version"""
    url = base_resource._build_url("friends", api_version="1.1")
    assert url == "https://api.fitbit.com/1.1/user/-/friends"


# -----------------------------------------------------------------------------
# 3. Calling Method Detection
# -----------------------------------------------------------------------------


def test_get_calling_method(base_resource):
    """Test getting the calling method name skips internal methods"""

    def wrapper_method():
        def _make_request():
            return base_resource._get_calling_method()

        return _make_request()

    method_name = wrapper_method()
    assert method_name == "wrapper_method"


@patch("fitbit_client.resources.base.currentframe")
def test_get_calling_method_with_frames(mock_frame, base_resource):
    """Test getting the calling method name with specific frame setup"""
    # Set up the frame chain: api_method -> _make_request -> _get_calling_method
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


def test_get_calling_method_unknown(base_resource):
    """Test fallback value when calling method can't be determined"""
    # This tests line 165 in base.py
    with patch("fitbit_client.resources.base.currentframe", return_value=None):
        method_name = base_resource._get_calling_method()
        assert method_name == "unknown"


# -----------------------------------------------------------------------------
# 4. Field Extraction
# -----------------------------------------------------------------------------


def test_extract_important_fields_with_list_of_dicts(base_resource):
    """Test extraction of fields from a list of dictionaries"""
    # This tests line 138-140 in base.py where it iterates over list items
    test_data = {
        "results": [
            {"id": 123, "name": "Activity 1", "details": {"type": "run"}},
            {"id": 456, "name": "Activity 2", "details": {"type": "swim"}},
        ]
    }

    result = base_resource._extract_important_fields(test_data)

    # Should extract both IDs with their indexed path
    assert result == {
        "results[0].id": 123,
        "results[0].name": "Activity 1",
        "results[1].id": 456,
        "results[1].name": "Activity 2",
    }


def test_extract_important_fields_with_nested_lists(base_resource):
    """Test extraction of fields from nested lists containing dictionaries"""
    test_data = {
        "activities": {
            "daily": [{"id": 123, "date": "2023-01-01"}, {"id": 456, "date": "2023-01-02"}]
        }
    }

    result = base_resource._extract_important_fields(test_data)

    assert result == {
        "activities.daily[0].id": 123,
        "activities.daily[0].date": "2023-01-01",
        "activities.daily[1].id": 456,
        "activities.daily[1].date": "2023-01-02",
    }


def test_extract_important_fields_with_mixed_list_items(base_resource):
    """Test that list iteration only processes dictionary items"""
    # This test specifically targets lines 138-139 in base.py
    # where it checks if each item in a list is a dictionary
    test_data = {
        "activities": [
            {"id": 123, "name": "Running"},
            "Not a dictionary",
            42,
            {"id": 456, "name": "Swimming"},
        ]
    }  # Dictionary item that should be processed  # String item that should be skipped  # Number item that should be skipped  # Dictionary item that should be processed

    result = base_resource._extract_important_fields(test_data)

    # Should only extract fields from the dictionary items
    assert result == {
        "activities[0].id": 123,
        "activities[0].name": "Running",
        "activities[3].id": 456,
        "activities[3].name": "Swimming",
    }

    # Also ensure non-dictionary items don't affect the extraction
    assert "activities[1]" not in result
    assert "activities[2]" not in result


# -----------------------------------------------------------------------------
# 5. Logging
# -----------------------------------------------------------------------------


def test_log_response_success(base_resource, mock_logger):
    """Test success logging"""
    response = Response()
    response.status_code = 200

    base_resource._log_response("test_method", "test/endpoint", response)
    mock_logger.info.assert_called_with("test_method succeeded for test/endpoint (status 200)")


def test_log_response_error_with_field(base_resource, mock_logger):
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


def test_log_response_error_without_field(base_resource, mock_logger):
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


def test_log_response_for_error_without_content(base_resource, mock_logger):
    """Test error logging when content isn't available"""
    # This tests line 260-263 in base.py
    mock_response = Mock()
    mock_response.status_code = 503

    base_resource._log_response("test_method", "test/endpoint", mock_response)

    # Assert error was logged with correct message
    mock_logger.error.assert_called_with(
        "Request failed for test/endpoint (method: test_method, status: 503)"
    )


# -----------------------------------------------------------------------------
# 6. Debug Mode Testing
# -----------------------------------------------------------------------------

# Debug mode tests are now in tests/utils/test_curl_debug_mixin.py


# -----------------------------------------------------------------------------
# 7. Response Handling
# -----------------------------------------------------------------------------


def test_handle_json_response(base_resource, mock_response):
    """Test JSON response handling"""
    mock_response.json.return_value = {"data": "test"}
    mock_response.status_code = 200

    result = base_resource._handle_json_response("test_method", "test/endpoint", mock_response)
    assert result == {"data": "test"}


def test_handle_json_response_invalid(base_resource, mock_response):
    """Test invalid JSON handling"""
    mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "doc", 0)
    mock_response.text = "Invalid {json"

    with raises(JSONDecodeError):
        base_resource._handle_json_response("test_method", "test/endpoint", mock_response)


def test_handle_json_response_with_invalid_json(base_resource, mock_logger):
    """Test handling of responses with invalid JSON"""
    # This provides additional coverage for the JSONDecodeError handling
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "doc", 0)

    with raises(JSONDecodeError):
        base_resource._handle_json_response("test_method", "test/endpoint", mock_response)

    # Verify the error was logged
    mock_logger.error.assert_called_once_with("Invalid JSON response from test/endpoint")


# -----------------------------------------------------------------------------
# 8. Request Making
# -----------------------------------------------------------------------------


def test_make_request_json_success(base_resource, mock_oauth_session, mock_response):
    """Test successful JSON request"""
    mock_response.json.return_value = {"success": True}
    mock_response.headers = {"content-type": "application/json"}
    mock_response.status_code = 200
    mock_oauth_session.request.return_value = mock_response

    result = base_resource._make_request("test/endpoint")
    assert result == {"success": True}


def test_make_request_no_content(base_resource, mock_oauth_session, mock_response):
    """Test request with no content"""
    mock_response.status_code = 204
    mock_response.headers = {}
    mock_response.json.return_value = {"success": True}
    mock_oauth_session.request.return_value = mock_response

    result = base_resource._make_request("test/endpoint")
    assert result is None


def test_make_request_xml_response(base_resource, mock_oauth_session, mock_response):
    """Test XML response handling"""
    mock_response.text = "<test>data</test>"
    mock_response.headers = {"content-type": "application/vnd.garmin.tcx+xml"}
    mock_response.status_code = 200
    mock_oauth_session.request.return_value = mock_response

    result = base_resource._make_request("test/endpoint")
    assert result == "<test>data</test>"


def test_make_request_unexpected_content_type(base_resource, mock_oauth_session, mock_response):
    """Test handling of unexpected content type"""
    mock_response.text = "some data"
    mock_response.headers = {"content-type": "text/plain"}
    mock_response.status_code = 200
    mock_oauth_session.request.return_value = mock_response

    result = base_resource._make_request("test/endpoint")
    assert result == None


def test_make_request_with_unexpected_exception(base_resource, mock_oauth_session, mock_logger):
    """Test handling of unexpected exceptions during request"""
    # This test covers line 458-461 in base.py
    mock_oauth_session.request.side_effect = ConnectionError("Network error")

    with raises(ConnectionError):
        base_resource._make_request("test/endpoint")

    # Verify the error was logged
    mock_logger.error.assert_called_once()
    log_message = mock_logger.error.call_args[0][0]
    assert "ConnectionError" in log_message
    assert "Network error" in log_message


# -----------------------------------------------------------------------------
# 9. Error Response Handling
# -----------------------------------------------------------------------------


def test_handle_error_response_with_non_json_error(base_resource, mock_logger):
    """Test handling of non-JSON error responses"""
    # Create a mock response that will fail to parse as JSON
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "doc", 0)

    # Test the error handling
    with raises(SystemException) as exc_info:
        base_resource._handle_error_response(mock_response)

    # Verify the exception
    assert exc_info.value.status_code == 500
    assert exc_info.value.error_type == "system"
    assert "Internal Server Error" in str(exc_info.value)

    # Verify logging happened correctly
    mock_logger.error.assert_called()
    log_call = mock_logger.error.call_args[0][0]
    assert "SystemException" in log_call
    assert "Internal Server Error" in log_call


def test_handle_error_response_with_empty_error_data(base_resource, mock_logger):
    """Test handling of error responses with empty error data"""
    # Create a mock response with empty JSON content
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.json.return_value = {}

    # Test the error handling
    with raises(FitbitAPIException) as exc_info:
        base_resource._handle_error_response(mock_response)

    # When json() returns an empty dict, we should expect the error_type to be "system"
    # and message to be "Unknown error" in the exception
    assert exc_info.value.status_code == 500
    assert exc_info.value.error_type == "system"
    assert "Unknown error" in str(exc_info.value)

    # The raw_response should be the same empty dict that was returned by json()
    assert exc_info.value.raw_response == {}


# -----------------------------------------------------------------------------
# 10. API Error Status Codes
# -----------------------------------------------------------------------------


def test_400_invalid_request(base_resource, mock_oauth_session, mock_response_factory):
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


def test_401_expired_token(base_resource, mock_oauth_session, mock_response_factory):
    """Test handling of 401 Unauthorized with expired token"""
    mock_response = mock_response_factory(
        401, {"errors": [{"errorType": "expired_token", "message": "Access token expired: ABC123"}]}
    )
    mock_oauth_session.request.return_value = mock_response

    with raises(ExpiredTokenException) as exc_info:
        base_resource._make_request("test/endpoint")

    assert exc_info.value.status_code == 401
    assert exc_info.value.error_type == "expired_token"
    assert "Access token expired" in str(exc_info.value)


def test_401_invalid_client(base_resource, mock_oauth_session, mock_response_factory):
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


def test_403_insufficient_scope(base_resource, mock_oauth_session, mock_response_factory):
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


def test_403_insufficient_permissions(base_resource, mock_oauth_session, mock_response_factory):
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


def test_404_not_found(base_resource, mock_oauth_session, mock_response_factory):
    """Test handling of 404 Not Found"""
    mock_response = mock_response_factory(
        404,
        {
            "errors": [
                {"errorType": "not_found", "message": "The resource with given id doesn't exist"}
            ]
        },
    )
    mock_oauth_session.request.return_value = mock_response

    with raises(NotFoundException) as exc_info:
        base_resource._make_request("test/endpoint")

    assert exc_info.value.status_code == 404
    assert exc_info.value.error_type == "not_found"


def test_429_rate_limit(base_resource, mock_oauth_session, mock_response_factory):
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


def test_validation_error_with_field(base_resource, mock_oauth_session, mock_response_factory):
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


def test_make_request_server_error(base_resource, mock_oauth_session, mock_response_factory):
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


def test_non_json_error_response(base_resource, mock_oauth_session, mock_response_factory):
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
    expected_response = {"errors": [{"errorType": "system", "message": "Internal Server Error"}]}
    assert exc_info.value.raw_response == expected_response


def test_error_with_empty_response(base_resource, mock_oauth_session, mock_response_factory):
    """Test handling of error responses with no content"""
    mock_response = mock_response_factory(502)
    mock_response.json.return_value = {}
    mock_oauth_session.request.return_value = mock_response

    with raises(FitbitAPIException) as exc_info:
        base_resource._make_request("test/endpoint")

    assert exc_info.value.status_code == 502
