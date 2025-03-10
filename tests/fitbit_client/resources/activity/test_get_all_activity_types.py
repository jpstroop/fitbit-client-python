# tests/fitbit_client/resources/activity/test_get_all_activity_types.py

"""Tests for the get_all_activity_types endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock


def test_get_all_activity_types(activity_resource):
    """Test getting all activity types"""
    activity_resource._make_request = Mock()
    activity_resource.get_all_activity_types()
    activity_resource._make_request.assert_called_once_with(
        "activities.json", requires_user_id=False, debug=False
    )
