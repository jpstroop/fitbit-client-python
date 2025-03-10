# tests/fitbit_client/resources/activity/test_delete_favorite_activity.py

"""Tests for the delete_favorite_activity endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock


def test_delete_favorite_activity(activity_resource):
    """Test deleting favorite activity"""
    activity_resource._make_request = Mock()
    activity_resource.delete_favorite_activity("123")
    activity_resource._make_request.assert_called_once_with(
        "activities/favorite/123.json", user_id="-", http_method="DELETE", debug=False
    )
