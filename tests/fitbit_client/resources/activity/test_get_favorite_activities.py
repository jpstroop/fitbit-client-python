# tests/fitbit_client/resources/activity/test_get_favorite_activities.py

"""Tests for the get_favorite_activities endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock


def test_get_favorite_activities(activity_resource):
    """Test getting favorite activities"""
    activity_resource._make_request = Mock()
    activity_resource.get_favorite_activities()
    activity_resource._make_request.assert_called_once_with(
        "activities/favorite.json", user_id="-", debug=False
    )
