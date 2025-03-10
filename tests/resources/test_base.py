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
# 10. Rate Limiting and Retry Logic
# -----------------------------------------------------------------------------


def test_get_retry_after_with_fitbit_header(base_resource):
    """Test that _get_retry_after correctly uses the Fitbit-Rate-Limit-Reset header."""
    mock_response = Mock()
    mock_response.headers = {"Fitbit-Rate-Limit-Reset": "600"}

    # Set up retry parameters
    base_resource.retry_after_seconds = 10
    base_resource.retry_backoff_factor = 2

    retry_seconds = base_resource._get_retry_after(mock_response, 1)

    # Should use the Fitbit-specific header value (600) instead of calculated backoff
    assert retry_seconds == 600


def test_get_retry_after_with_retry_after_header(base_resource):
    """Test that _get_retry_after correctly uses the Retry-After header when Fitbit header is missing."""
    mock_response = Mock()
    mock_response.headers = {"Retry-After": "30"}

    # Set up retry parameters
    base_resource.retry_after_seconds = 10
    base_resource.retry_backoff_factor = 2

    retry_seconds = base_resource._get_retry_after(mock_response, 1)

    # Should use the Retry-After header value (30) instead of calculated backoff
    assert retry_seconds == 30


def test_get_retry_after_with_invalid_header(base_resource):
    """Test that _get_retry_after falls back to calculated backoff when Retry-After header is not a digit."""
    mock_response = Mock()
    mock_response.headers = {"Retry-After": "not-a-number"}

    # Set up retry parameters
    base_resource.retry_after_seconds = 10
    base_resource.retry_backoff_factor = 2

    # For retry_count=1, should be 10 * (2^1) = 20
    retry_seconds = base_resource._get_retry_after(mock_response, 1)

    # Should use calculated backoff
    assert retry_seconds == 20


def test_get_retry_after_without_header(base_resource):
    """Test that _get_retry_after falls back to calculated backoff when Retry-After header is missing."""
    mock_response = Mock()
    mock_response.headers = {}  # No Retry-After header

    # Set up retry parameters
    base_resource.retry_after_seconds = 10
    base_resource.retry_backoff_factor = 2

    # For retry_count=0, should be 10 * (2^0) = 10
    retry_seconds = base_resource._get_retry_after(mock_response, 0)

    # Should use calculated backoff
    assert retry_seconds == 10


@patch("fitbit_client.resources.base.sleep")
def test_rate_limit_retries(
    mock_sleep, base_resource, mock_oauth_session, mock_response_factory, mock_logger
):
    """Test that rate limiting exceptions cause retries with backoff"""
    # Configure the resource with custom retry settings
    base_resource.max_retries = 2
    base_resource.retry_after_seconds = 10
    base_resource.retry_backoff_factor = 2.0

    # Create rate limit error response
    rate_limit_response = mock_response_factory(
        429, {"errors": [{"errorType": "rate_limit_exceeded", "message": "Too many requests"}]}
    )

    # Create success response for after retry
    success_response = mock_response_factory(200, {"data": "success"})

    # Set up mock to return rate limit error first, then success
    mock_oauth_session.request.side_effect = [rate_limit_response, success_response]

    # Make the request that will initially fail but then retry and succeed
    result = base_resource._make_request("test/endpoint")

    # Verify the result after retry is successful
    assert result == {"data": "success"}

    # Verify retry was logged
    assert mock_logger.warning.call_count == 1
    assert "Rate limit exceeded" in mock_logger.warning.call_args[0][0]

    # Verify sleep was called with the expected backoff value (10 seconds)
    mock_sleep.assert_called_once_with(10)

    # Verify request was called twice (initial + retry)
    assert mock_oauth_session.request.call_count == 2


@patch("fitbit_client.resources.base.sleep")
def test_rate_limit_retry_with_backoff(
    mock_sleep, base_resource, mock_oauth_session, mock_response_factory
):
    """Test backoff strategy when no Retry-After header is provided"""
    # Configure the resource with custom retry settings
    base_resource.max_retries = 2
    base_resource.retry_after_seconds = 10
    base_resource.retry_backoff_factor = 2.0

    # Create two rate limit error responses without Retry-After headers
    rate_limit_response1 = mock_response_factory(
        429, {"errors": [{"errorType": "rate_limit_exceeded", "message": "Too many requests"}]}
    )

    rate_limit_response2 = mock_response_factory(
        429, {"errors": [{"errorType": "rate_limit_exceeded", "message": "Too many requests"}]}
    )

    # Create success response for after retries
    success_response = mock_response_factory(200, {"data": "success"})

    # Set up mock to return rate limit errors twice, then success
    mock_oauth_session.request.side_effect = [
        rate_limit_response1,
        rate_limit_response2,
        success_response,
    ]

    # Make the request that will fail twice but then succeed
    result = base_resource._make_request("test/endpoint")

    # Verify the result after retries is successful
    assert result == {"data": "success"}

    # Verify exponential backoff was used (10 seconds, then 10*2 = 20 seconds)
    assert mock_sleep.call_count == 2
    assert mock_sleep.call_args_list[0][0][0] == 10  # First retry: base wait time
    assert mock_sleep.call_args_list[1][0][0] == 20  # Second retry: base time * backoff factor

    # Verify request was called three times (initial + 2 retries)
    assert mock_oauth_session.request.call_count == 3


@patch("fitbit_client.resources.base.sleep")
def test_rate_limit_max_retries_exhausted(
    mock_sleep, base_resource, mock_oauth_session, mock_response_factory
):
    """Test exception is raised when max retries are exhausted"""
    # Configure the resource with custom retry settings
    base_resource.max_retries = 2
    base_resource.retry_after_seconds = 5
    base_resource.retry_backoff_factor = 1.5

    # Create rate limit error responses
    rate_limit_response = mock_response_factory(
        429, {"errors": [{"errorType": "rate_limit_exceeded", "message": "Too many requests"}]}
    )

    # Set up mock to return rate limit errors for all requests
    mock_oauth_session.request.side_effect = [
        rate_limit_response,
        rate_limit_response,
        rate_limit_response,
    ]

    # Make the request that will fail and exhaust all retries
    with raises(RateLimitExceededException) as exc_info:
        base_resource._make_request("test/endpoint")

    # Verify the exception is a rate limit exception
    assert exc_info.value.status_code == 429
    assert exc_info.value.error_type == "rate_limit_exceeded"

    # Verify retry was attempted the expected number of times
    assert mock_sleep.call_count == 2

    # Verify request was made the expected number of times (initial + 2 retries)
    assert mock_oauth_session.request.call_count == 3


# -----------------------------------------------------------------------------
# 11. Direct Request Testing
# -----------------------------------------------------------------------------


@patch("builtins.print")
@patch("fitbit_client.resources.base.CurlDebugMixin._build_curl_command")
def test_make_direct_request_with_debug(mock_build_curl, mock_print, base_resource):
    """Test that _make_direct_request returns empty dict when debug=True."""
    # Mock the _build_curl_command method
    mock_build_curl.return_value = "curl -X GET https://example.com"

    # Mock the _get_calling_method to test complete debug output
    with patch.object(base_resource, "_get_calling_method", return_value="test_pagination"):
        # Call the method with debug=True
        result = base_resource._make_direct_request("/test", debug=True)

        # Should return empty dict in debug mode
        assert result == {}

        # Verify the curl command was built correctly
        mock_build_curl.assert_called_once_with("https://api.fitbit.com/test", "GET")

        # Verify print was called with the right message pattern
        mock_print.assert_any_call("\n# Debug curl command for test_pagination (pagination):")


@patch("fitbit_client.resources.base.BaseResource._handle_json_response")
def test_make_direct_request_success(mock_handle_json, base_resource):
    """Test successful direct request with JSON response."""
    # Mock the OAuth session
    base_resource.oauth = Mock()

    # Create a mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "application/json"}
    base_resource.oauth.request.return_value = mock_response

    # Mock the _handle_json_response method
    mock_handle_json.return_value = {"data": "test"}

    # Call the method
    result = base_resource._make_direct_request("/test")

    # Should return the JSON data
    assert result == {"data": "test"}

    # Verify the request was made
    base_resource.oauth.request.assert_called_once()
    mock_handle_json.assert_called_once()


@patch("fitbit_client.resources.base.BaseResource._get_calling_method")
def test_make_direct_request_unexpected_content_type(mock_get_calling, base_resource, mock_logger):
    """Test handling of unexpected content type in direct request."""
    mock_get_calling.return_value = "test_method"

    # Mock the OAuth session
    base_resource.oauth = Mock()

    # Create a mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "text/plain"}
    base_resource.oauth.request.return_value = mock_response

    # Call the method
    result = base_resource._make_direct_request("/test")

    # Should return empty dict for unexpected content type
    assert result == {}

    # Should log an error about unexpected content type
    mock_logger.error.assert_called_once()
    assert "Unexpected content type" in mock_logger.error.call_args[0][0]


@patch("fitbit_client.resources.base.sleep")
@patch("fitbit_client.resources.base.BaseResource._get_retry_after")
def test_direct_request_rate_limit_retry(mock_get_retry, mock_sleep, base_resource, mock_logger):
    """Test rate limit retry for direct requests."""

    rate_limit_response = Mock()
    rate_limit_response.status_code = 429
    rate_limit_response.headers = {
        "Fitbit-Rate-Limit-Limit": "150",
        "Fitbit-Rate-Limit-Remaining": "0",
        "Fitbit-Rate-Limit-Reset": "3600",
    }

    success_response = Mock()
    success_response.status_code = 200
    success_response.headers = {"content-type": "application/json"}
    success_response.json.return_value = {"data": "success"}

    # Mock the OAuth session and calling method
    with patch.object(base_resource, "_get_calling_method", return_value="test_method"):
        base_resource.oauth = Mock()
        base_resource.oauth.request.side_effect = [rate_limit_response, success_response]

        # Create a RateLimitExceededException with rate limit info
        rate_limit_exception = RateLimitExceededException(
            message="Too many requests",
            error_type="rate_limit_exceeded",
            status_code=429,
            rate_limit=150,
            rate_limit_remaining=0,
            rate_limit_reset=3600,
        )

        # Make _handle_error_response raise the exception
        with patch.object(
            base_resource, "_handle_error_response", side_effect=[rate_limit_exception, None]
        ):
            # Set up retry
            base_resource.max_retries = 1
            mock_get_retry.return_value = 10

            # Make the direct request
            result = base_resource._make_direct_request("/test")

            # Verify results
            assert result == {"data": "success"}
            assert base_resource.oauth.request.call_count == 2
            assert mock_sleep.call_count == 1

            # Verify log includes rate limit info in warning message
            for call in mock_logger.warning.call_args_list:
                call_args = call[0][0]
                if "Rate limit exceeded" in call_args and "pagination request" in call_args:
                    assert "[Rate Limit: 0/150]" in call_args
                    break
            else:
                assert False, "Rate limit warning log not found"


@patch("fitbit_client.resources.base.sleep")
@patch("fitbit_client.resources.base.BaseResource._handle_error_response")
@patch("fitbit_client.resources.base.BaseResource._should_retry_request")
def test_make_direct_request_rate_limit_retry(
    mock_should_retry, mock_handle_error, mock_sleep, base_resource, mock_logger
):
    """Test retry behavior for rate-limited requests."""
    # Configure the resource with custom retry settings
    base_resource.max_retries = 1
    base_resource.retry_after_seconds = 10
    base_resource.retry_backoff_factor = 1

    # Mock the OAuth session
    base_resource.oauth = Mock()

    # Create a mock response for error and success
    error_response = Mock()
    error_response.status_code = 429
    error_response.headers = {"Retry-After": "5"}

    success_response = Mock()
    success_response.status_code = 200
    success_response.headers = {"content-type": "application/json"}
    success_response.json.return_value = {"data": "success"}

    # Set up the mock to return error first, then success
    base_resource.oauth.request.side_effect = [error_response, success_response]

    # Set up mocks for retry logic
    mock_handle_error.side_effect = RateLimitExceededException(
        message="Too many requests", status_code=429, error_type="rate_limit_exceeded"
    )
    mock_should_retry.return_value = True

    # Call the method
    with patch(
        "fitbit_client.resources.base.BaseResource._handle_json_response"
    ) as mock_handle_json:
        mock_handle_json.return_value = {"data": "success"}
        result = base_resource._make_direct_request("/test")

    # Verify results
    assert result == {"data": "success"}
    assert base_resource.oauth.request.call_count == 2
    assert mock_sleep.call_count == 1
    assert mock_logger.warning.call_count == 1


@patch("fitbit_client.resources.base.BaseResource._get_calling_method")
def test_make_direct_request_exception(mock_get_calling, base_resource, mock_logger):
    """Test handling of exceptions in direct request."""
    mock_get_calling.return_value = "test_method"

    # Mock the OAuth session
    base_resource.oauth = Mock()
    base_resource.oauth.request.side_effect = ConnectionError("Network error")

    # Call the method
    with raises(Exception) as exc_info:
        base_resource._make_direct_request("/test")

    # Verify exception and logging
    assert "Pagination request failed" in str(exc_info.value)
    assert mock_logger.error.call_count == 1


# -----------------------------------------------------------------------------
# 12. API Error Status Codes
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

    # Create response with Fitbit rate limit headers
    mock_response = mock_response_factory(429, error_response, content_type="application/json")
    mock_response.headers.update(
        {
            "Fitbit-Rate-Limit-Limit": "150",
            "Fitbit-Rate-Limit-Remaining": "0",
            "Fitbit-Rate-Limit-Reset": "3600",
        }
    )

    # Important: We need to set a simple side_effect rather than return_value to prevent retries
    # which might cause the test to hang
    mock_oauth_session.request.side_effect = [mock_response]

    # Set retries to 0 to prevent the test from attempting retries
    base_resource.max_retries = 0

    with raises(RateLimitExceededException) as exc_info:
        base_resource._make_request("test/endpoint")

    assert exc_info.value.status_code == 429
    assert exc_info.value.error_type == "rate_limit_exceeded"
    assert exc_info.value.raw_response == error_response
    assert "Too many requests" in str(exc_info.value)

    # Check that rate limit headers were correctly parsed and stored
    assert exc_info.value.rate_limit == 150
    assert exc_info.value.rate_limit_remaining == 0
    assert exc_info.value.rate_limit_reset == 3600

    # Verify that the response object is stored for retry logic
    assert exc_info.value.response is mock_response


def test_log_data_with_important_fields(base_resource, mock_response, mock_logger):
    """Test that _log_data properly logs important fields from response content."""
    # This tests lines 283-288 in base.py
    mock_content = {"activities": [{"id": 123, "name": "Running", "date": "2023-01-01"}]}

    # Create a data_logger to test
    data_logger_mock = Mock()
    base_resource.data_logger = data_logger_mock

    # Call the method
    base_resource._log_data("test_method", mock_content)

    # Verify the data logger was called with a JSON string
    data_logger_mock.info.assert_called_once()
    log_entry = data_logger_mock.info.call_args[0][0]

    # Verify the log entry is a valid JSON string with the expected structure
    # Standard library imports
    import json

    parsed_log = json.loads(log_entry)
    assert "timestamp" in parsed_log
    assert parsed_log["method"] == "test_method"
    assert parsed_log["fields"]["activities[0].id"] == 123
    assert parsed_log["fields"]["activities[0].name"] == "Running"
    assert parsed_log["fields"]["activities[0].date"] == "2023-01-01"


def test_rate_limit_headers_logging(base_resource, mock_logger):
    """Test that rate limit headers are properly logged on successful requests."""
    # This tests lines 657-659 in base.py
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {
        "content-type": "application/json",
        "Fitbit-Rate-Limit-Limit": "150",
        "Fitbit-Rate-Limit-Remaining": "120",
        "Fitbit-Rate-Limit-Reset": "1800",
    }
    mock_response.json.return_value = {"data": "test"}

    base_resource.oauth = Mock()
    base_resource.oauth.request.return_value = mock_response

    result = base_resource._make_request("test/endpoint")

    # Verify the debug log contains rate limit information
    for call in mock_logger.debug.call_args_list:
        call_args = call[0][0]
        if "Rate limit status" in call_args:
            assert "120/150" in call_args
            assert "1800s" in call_args
            break
    else:
        assert False, "Rate limit status log not found"


@patch("fitbit_client.resources.base.sleep")
def test_rate_limit_retry_with_fitbit_headers(
    mock_sleep, base_resource, mock_oauth_session, mock_logger
):
    """Test that rate limit retry correctly uses Fitbit headers for retry timing."""
    rate_limit_response = Mock()
    rate_limit_response.status_code = 429
    rate_limit_response.headers = {
        "Fitbit-Rate-Limit-Limit": "150",
        "Fitbit-Rate-Limit-Remaining": "0",
        "Fitbit-Rate-Limit-Reset": "3600",
    }

    success_response = Mock()
    success_response.status_code = 200
    success_response.headers = {"content-type": "application/json"}
    success_response.json.return_value = {"data": "success"}

    # Set up side effects
    mock_oauth_session.request.side_effect = [rate_limit_response, success_response]

    # Create a RateLimitExceededException with rate limit info and response object
    rate_limit_exception = RateLimitExceededException(
        message="Too many requests",
        error_type="rate_limit_exceeded",
        status_code=429,
        rate_limit=150,
        rate_limit_remaining=0,
        rate_limit_reset=3600,
        response=rate_limit_response,
    )

    # Make _handle_error_response raise the exception
    with patch.object(
        base_resource, "_handle_error_response", side_effect=[rate_limit_exception, None]
    ):
        # Set up retry
        base_resource.max_retries = 1

        # Make the request
        result = base_resource._make_request("test/endpoint")

        # Verify results
        assert result == {"data": "success"}
        assert mock_oauth_session.request.call_count == 2
        assert mock_sleep.call_count == 1

        # Verify the sleep was called with the Fitbit-Rate-Limit-Reset value
        mock_sleep.assert_called_once_with(3600)

        # Verify log includes rate limit info
        for call in mock_logger.warning.call_args_list:
            call_args = call[0][0]
            if "Rate limit exceeded" in call_args:
                assert "[Rate Limit: 0/150]" in call_args
                assert "Retrying in 3600 seconds" in call_args
                break
        else:
            assert False, "Rate limit warning log not found"


@patch("fitbit_client.resources.base.sleep")
def test_rate_limit_retry_without_response(
    mock_sleep, base_resource, mock_oauth_session, mock_logger
):
    """Test retry for rate limit errors without a response object (fallback path)."""
    error_response = Mock()
    error_response.status_code = 429
    error_response.headers = {}  # No headers

    # Set up side effects - only return error to force exception
    mock_oauth_session.request.side_effect = lambda *args, **kwargs: error_response

    # Create a RateLimitExceededException WITHOUT a response object
    rate_limit_exception = RateLimitExceededException(
        message="Too many requests",
        error_type="rate_limit_exceeded",
        status_code=429,
        rate_limit=150,
        rate_limit_remaining=0,
        rate_limit_reset=3600,
        # No response object provided
    )

    # Make _handle_error_response raise the exception
    with patch.object(base_resource, "_handle_error_response", side_effect=rate_limit_exception):
        # Set up retry
        base_resource.max_retries = 1
        base_resource.retry_after_seconds = 60
        base_resource.retry_backoff_factor = 1.5

        # Make the request - it will fail after one retry
        with raises(RateLimitExceededException):
            base_resource._make_request("test/endpoint")

        # Verify the sleep was called with the fallback exponential backoff
        mock_sleep.assert_called_once_with(60)  # First retry is just base value


@patch("fitbit_client.resources.base.sleep")
def test_direct_request_retry_without_response(mock_sleep, base_resource, mock_logger):
    """Test direct request retry for rate limit errors without a response object."""
    error_response = Mock()
    error_response.status_code = 429
    error_response.headers = {}  # No headers

    # Mock the OAuth session to always return an error response
    base_resource.oauth = Mock()
    base_resource.oauth.request.side_effect = lambda *args, **kwargs: error_response

    # Create a RateLimitExceededException WITHOUT a response object
    rate_limit_exception = RateLimitExceededException(
        message="Too many requests",
        error_type="rate_limit_exceeded",
        status_code=429,
        rate_limit=150,
        rate_limit_remaining=0,
        rate_limit_reset=3600,
        # No response object provided
    )

    # Make _handle_error_response raise the exception
    with (
        patch.object(base_resource, "_handle_error_response", side_effect=rate_limit_exception),
        patch.object(base_resource, "_get_calling_method", return_value="test_method"),
    ):
        # Set up retry
        base_resource.max_retries = 1
        base_resource.retry_after_seconds = 60
        base_resource.retry_backoff_factor = 1.5

        # We expect to get an exception because we only set up error responses
        with raises(Exception):  # Just use base Exception to be simpler
            base_resource._make_direct_request("/test/path")

        # Verify the sleep was called with the fallback exponential backoff
        mock_sleep.assert_called_once_with(60)  # Just the base value for first retry


@patch("fitbit_client.resources.base.sleep")
@patch("fitbit_client.resources.base.BaseResource._get_retry_after")
def test_direct_request_retry_with_fitbit_headers(
    mock_get_retry, mock_sleep, base_resource, mock_logger
):
    """Test direct request retry with Fitbit rate limit headers."""
    # Set up two responses - error first, then success
    error_response = Mock()
    error_response.status_code = 429
    error_response.headers = {
        "Fitbit-Rate-Limit-Limit": "150",
        "Fitbit-Rate-Limit-Remaining": "0",
        "Fitbit-Rate-Limit-Reset": "3600",
    }

    success_response = Mock()
    success_response.status_code = 200
    success_response.headers = {"content-type": "application/json"}
    success_response.json.return_value = {"data": "success"}

    # Mock the OAuth session
    base_resource.oauth = Mock()
    base_resource.oauth.request.side_effect = [error_response, success_response]

    # Create a RateLimitExceededException WITH response object
    rate_limit_exception = RateLimitExceededException(
        message="Too many requests",
        error_type="rate_limit_exceeded",
        status_code=429,
        rate_limit=150,
        rate_limit_remaining=0,
        rate_limit_reset=3600,
        response=error_response,
    )

    # Mock _get_retry_after to return a known value
    mock_get_retry.return_value = 3600

    # Make _handle_error_response raise the exception once, then return None
    with (
        patch.object(
            base_resource, "_handle_error_response", side_effect=[rate_limit_exception, None]
        ),
        patch.object(base_resource, "_get_calling_method", return_value="test_method"),
    ):
        # Set up retry
        base_resource.max_retries = 1

        # Make the request - should succeed on second try
        result = base_resource._make_direct_request("/test/path")

        # Verify results
        assert result == {"data": "success"}
        assert base_resource.oauth.request.call_count == 2
        assert mock_sleep.call_count == 1

        # Verify _get_retry_after was called with the response
        mock_get_retry.assert_called_once_with(error_response, 0)

        # Verify sleep was called with the correct value
        mock_sleep.assert_called_once_with(3600)


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
