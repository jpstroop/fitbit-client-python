# tests/resources/test_subscription.py

# Standard library imports
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.subscription import SubscriptionResource


class TestSubscriptionResource:
    @fixture
    def subscription_resource(self):
        """Create a SubscriptionResource with mocked OAuth session"""
        mock_oauth = Mock()
        with patch("fitbit_client.resources.base.getLogger"):
            return SubscriptionResource(mock_oauth, "en_US", "en_US")

    def test_create_subscription_validates_id_length(self, subscription_resource):
        """Test that subscription_id length is validated"""
        long_id = "x" * 51  # Create 51 character string

        with raises(ValidationException) as exc_info:
            subscription_resource.create_subscription(long_id)

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_type == "validation"
        assert exc_info.value.field_name == "subscription_id"
        assert "must not exceed 50 characters" in str(exc_info.value)

    def test_create_subscription_allows_valid_id_length(self, subscription_resource):
        """Test that valid subscription_id lengths are allowed"""
        valid_id = "x" * 50  # Create 50 character string

        # Mock the _make_request to avoid actual API call
        subscription_resource._make_request = Mock()

        # Should not raise an exception
        subscription_resource.create_subscription(valid_id)
