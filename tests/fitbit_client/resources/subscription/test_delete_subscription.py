# tests/fitbit_client/resources/subscription/test_delete_subscription.py

"""Tests for the delete_subscription endpoint."""

# Third party imports

# Third party imports
from pytest import raises


def test_delete_subscription_not_implemented(subscription_resource):
    """Test that delete_subscription raises NotImplementedError"""
    with raises(NotImplementedError):
        subscription_resource.delete_subscription("test-id")
