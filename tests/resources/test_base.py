# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.base import BaseResource


class TestBaseResource:
    @fixture
    def base_resource(self, mock_oauth_session):
        """Fixture to provide a BaseResource instance"""
        return BaseResource(oauth_session=mock_oauth_session, locale="en_US", language="en_US")

    def test_build_url_with_user_id(self, base_resource):
        """Test URL building with user endpoint"""
        url = base_resource._build_url("test/endpoint", user_id="123")
        assert url == "https://api.fitbit.com/1/user/123/test/endpoint"

    def test_build_url_without_user_id(self, base_resource):
        """Test URL building with public endpoint"""
        url = base_resource._build_url("test/endpoint", requires_user_id=False)
        assert url == "https://api.fitbit.com/1/test/endpoint"

    def test_make_request(self, base_resource, mock_oauth_session, mock_response):
        """Test making a basic GET request"""
        mock_oauth_session.request.return_value = mock_response

        result = base_resource._make_request("test/endpoint")

        mock_oauth_session.request.assert_called_once_with(
            "GET",
            "https://api.fitbit.com/1/user/-/test/endpoint",
            data=None,
            json=None,
            params=None,
            headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        )

        assert result == {"status": 200, "headers": {}, "content": {"success": True}}
