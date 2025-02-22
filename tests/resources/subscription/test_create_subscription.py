# tests/resources/subscription/test_create_subscription.py

"""Tests for the create_subscription endpoint."""

# Third party imports

# Third party imports
from pytest import raises


def test_create_subscription_not_implemented(subscription_resource):
    """Test that create_subscription raises NotImplementedError"""
    with raises(NotImplementedError):
        subscription_resource.create_subscription("test-id")
