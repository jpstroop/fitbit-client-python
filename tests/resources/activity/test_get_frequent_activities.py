# tests/resources/activity/test_get_frequent_activities.py

"""Tests for the get_frequent_activities endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock


def test_get_frequent_activities(activity_resource):
    """Test getting frequent activities"""
    activity_resource._make_request = Mock()
    activity_resource.get_frequent_activities()
    activity_resource._make_request.assert_called_once_with(
        "activities/frequent.json", user_id="-", debug=False
    )
