# tests/fitbit_client/resources/subscription/test_get_subscription_list.py

"""Tests for the get_subscription_list endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock

# Local imports
from fitbit_client.resources._constants import SubscriptionCategory


def test_get_subscription_list_success(subscription_resource):
    """Test successful retrieval of subscription list"""
    subscription_resource._make_request = Mock()
    subscription_resource.get_subscription_list()
    subscription_resource._make_request.assert_called_once_with(
        "apiSubscriptions.json", user_id="-", headers={}, debug=False
    )


def test_get_subscription_list_with_category(subscription_resource):
    """Test retrieving subscriptions for specific category"""
    subscription_resource._make_request = Mock()
    subscription_resource.get_subscription_list(category=SubscriptionCategory.ACTIVITIES)
    subscription_resource._make_request.assert_called_once_with(
        "activities/apiSubscriptions.json", user_id="-", headers={}, debug=False
    )


def test_get_subscription_list_with_subscriber_id(subscription_resource):
    """Test retrieving subscriptions with subscriber ID"""
    subscription_resource._make_request = Mock()
    subscription_resource.get_subscription_list(subscriber_id="test-subscriber")
    subscription_resource._make_request.assert_called_once_with(
        "apiSubscriptions.json",
        user_id="-",
        headers={"X-Fitbit-Subscriber-Id": "test-subscriber"},
        debug=False,
    )


def test_get_subscription_list_with_custom_user(subscription_resource):
    """Test retrieving subscriptions for specific user"""
    subscription_resource._make_request = Mock()
    subscription_resource.get_subscription_list(user_id="123ABC")
    subscription_resource._make_request.assert_called_once_with(
        "apiSubscriptions.json", user_id="123ABC", headers={}, debug=False
    )
