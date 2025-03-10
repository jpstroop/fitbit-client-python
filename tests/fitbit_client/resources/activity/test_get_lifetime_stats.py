# tests/fitbit_client/resources/activity/test_get_lifetime_stats.py

"""Tests for the get_lifetime_stats endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock


def test_get_lifetime_stats(activity_resource):
    """Test getting lifetime stats"""
    activity_resource._make_request = Mock()
    activity_resource.get_lifetime_stats()
    activity_resource._make_request.assert_called_once_with(
        "activities.json", user_id="-", debug=False
    )
