# tests/fitbit_client/resources/activity/test_get_recent_activity_types.py

"""Tests for the get_recent_activity_types endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock


def test_get_recent_activity_types(activity_resource):
    """Test getting recent activities"""
    activity_resource._make_request = Mock()
    activity_resource.get_recent_activity_types()
    activity_resource._make_request.assert_called_once_with(
        "activities/recent.json", user_id="-", debug=False
    )
