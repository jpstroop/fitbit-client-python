# tests/fitbit_client/resources/activity/test_create_favorite_activity.py

"""Tests for the create_favorite_activity endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock


def test_create_favorite_activity(activity_resource):
    """Test creating favorite activity"""
    activity_resource._make_request = Mock()
    activity_resource.create_favorite_activity("123")
    activity_resource._make_request.assert_called_once_with(
        "activities/favorite/123.json", user_id="-", http_method="POST", debug=False
    )
