# tests/resources/activity/test_get_activity_type.py

"""Tests for the get_activity_type endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock


def test_get_activity_type(activity_resource):
    """Test getting activity type"""
    activity_resource._make_request = Mock()
    activity_resource.get_activity_type("123")
    activity_resource._make_request.assert_called_once_with(
        "activities/123.json", requires_user_id=False, debug=False
    )
