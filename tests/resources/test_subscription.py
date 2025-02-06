# tests/resources/test_subscription.py

# Standard library imports
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from pytest import raises

# Local imports
from fitbit_client.resources.constants import SubscriptionCategory
from fitbit_client.resources.subscription import SubscriptionResource


class TestSubscriptionResource:
    @fixture
    def subscription_resource(self):
        """Create a SubscriptionResource with mocked OAuth session"""
        mock_oauth = Mock()
        with patch("fitbit_client.resources.base.getLogger"):
            return SubscriptionResource(mock_oauth, "en_US", "en_US")

    def test_get_subscription_list_success(self, subscription_resource):
        """Test successful retrieval of subscription list"""
        subscription_resource._make_request = Mock()
        subscription_resource.get_subscription_list()

        subscription_resource._make_request.assert_called_once_with(
            "apiSubscriptions.json", user_id="-", headers={}, debug=False
        )

    def test_get_subscription_list_with_category(self, subscription_resource):
        """Test retrieving subscriptions for specific category"""
        subscription_resource._make_request = Mock()
        subscription_resource.get_subscription_list(category=SubscriptionCategory.ACTIVITIES)

        subscription_resource._make_request.assert_called_once_with(
            "activities/apiSubscriptions.json", user_id="-", headers={}, debug=False
        )

    def test_get_subscription_list_with_subscriber_id(self, subscription_resource):
        """Test retrieving subscriptions with subscriber ID"""
        subscription_resource._make_request = Mock()
        subscription_resource.get_subscription_list(subscriber_id="test-subscriber")

        subscription_resource._make_request.assert_called_once_with(
            "apiSubscriptions.json",
            user_id="-",
            headers={"X-Fitbit-Subscriber-Id": "test-subscriber"},
            debug=False,
        )

    def test_get_subscription_list_with_custom_user(self, subscription_resource):
        """Test retrieving subscriptions for specific user"""
        subscription_resource._make_request = Mock()
        subscription_resource.get_subscription_list(user_id="123ABC")

        subscription_resource._make_request.assert_called_once_with(
            "apiSubscriptions.json", user_id="123ABC", headers={}, debug=False
        )

    def test_create_subscription_not_implemented(self, subscription_resource):
        """Test that create_subscription raises NotImplementedError"""
        with raises(NotImplementedError):
            subscription_resource.create_subscription("test-id")

    def test_delete_subscription_not_implemented(self, subscription_resource):
        """Test that delete_subscription raises NotImplementedError"""
        with raises(NotImplementedError):
            subscription_resource.delete_subscription("test-id")
