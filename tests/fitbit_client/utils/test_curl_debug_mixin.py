# tests/fitbit_client/utils/test_curl_debug_mixin.py

"""Tests for CurlDebugMixin"""

# Standard library imports
from unittest.mock import Mock

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.utils.curl_debug_mixin import CurlDebugMixin


# Create a test class that uses the mixin for debug testing
# Using a function to create the test class to avoid pytest collection warning
def create_test_resource_class():
    class TestResource(CurlDebugMixin):
        """Test class that uses CurlDebugMixin"""

        def __init__(self):
            self.oauth = Mock()
            self.oauth.token = {"access_token": "test_token"}

        def make_debug_request(self, debug=False):
            """Test method that simulates _make_request with debug mode"""
            url = "https://api.fitbit.com/1/user/-/test/endpoint"

            if debug:
                curl_command = self._build_curl_command(
                    url=url, http_method="GET", params={"param1": "value1"}
                )
                print(f"\n# Debug curl command:")
                print(curl_command)
                print()
                return None

            return {"success": True}

    return TestResource


@fixture
def curl_debug_mixin():
    """Fixture for CurlDebugMixin with mocked OAuth session"""
    mixin = CurlDebugMixin()
    mixin.oauth = Mock()
    mixin.oauth.token = {"access_token": "test_token"}
    return mixin


def test_build_curl_command_with_json_data(curl_debug_mixin):
    """Test generating curl command with JSON data"""
    json_data = {"name": "Test Activity", "type": "run", "duration": 3600}
    result = curl_debug_mixin._build_curl_command(
        url="https://api.fitbit.com/1/user/-/activities.json", http_method="POST", json=json_data
    )

    # Assert command contains JSON data and correct header
    assert '-d \'{"name": "Test Activity", "type": "run", "duration": 3600}\'' in result
    assert '-H "Content-Type: application/json"' in result
    assert "-X POST" in result
    assert "curl -v" in result
    assert '-H "Authorization: Bearer test_token"' in result
    assert "'https://api.fitbit.com/1/user/-/activities.json'" in result


def test_build_curl_command_with_form_data(curl_debug_mixin):
    """Test generating curl command with form data"""
    form_data = {"date": "2023-01-01", "foodId": "12345", "amount": "1", "mealTypeId": "1"}
    result = curl_debug_mixin._build_curl_command(
        url="https://api.fitbit.com/1/user/-/foods/log.json", http_method="POST", data=form_data
    )

    # Assert command contains form data and correct header
    assert "-d 'date=2023-01-01&foodId=12345&amount=1&mealTypeId=1'" in result
    assert '-H "Content-Type: application/x-www-form-urlencoded"' in result
    assert "-X POST" in result


def test_build_curl_command_with_get_params(curl_debug_mixin):
    """Test generating curl command with GET parameters"""
    params = {"date": "2023-01-01", "offset": "0", "limit": "10"}
    result = curl_debug_mixin._build_curl_command(
        url="https://api.fitbit.com/1/user/-/activities/list.json", http_method="GET", params=params
    )

    # Assert command doesn't have -X GET but has parameters in URL
    assert "-X GET" not in result
    assert "?date=2023-01-01&offset=0&limit=10" in result


def test_build_curl_command_with_delete(curl_debug_mixin):
    """Test generating curl command for DELETE request"""
    result = curl_debug_mixin._build_curl_command(
        url="https://api.fitbit.com/1/user/-/foods/log/123456.json", http_method="DELETE"
    )

    # Assert command has DELETE method
    assert "-X DELETE" in result
    assert "curl -v" in result
    assert '-H "Authorization: Bearer test_token"' in result


def test_debug_mode_integration(capsys):
    """Test debug mode integration with a resource class"""
    # Create test resource class and instance
    TestResource = create_test_resource_class()
    resource = TestResource()

    # Call make_debug_request with debug=True
    result = resource.make_debug_request(debug=True)

    # Capture stdout
    captured = capsys.readouterr()

    # Verify results
    assert result is None
    assert "curl" in captured.out
    assert "test/endpoint" in captured.out
    assert "param1=value1" in captured.out
    assert "test_token" in captured.out


def test_build_curl_command_without_oauth():
    """Test curl command generation when oauth is not available"""
    # Create a bare mixin instance without oauth
    mixin = CurlDebugMixin()

    # Generate a curl command
    result = mixin._build_curl_command(
        url="https://api.fitbit.com/1/user/-/test.json", http_method="GET"
    )

    # Verify that the fallback auth header is used
    assert '-H "Authorization: Bearer TOKEN"' in result
    assert "curl -v" in result
    assert "'https://api.fitbit.com/1/user/-/test.json'" in result
