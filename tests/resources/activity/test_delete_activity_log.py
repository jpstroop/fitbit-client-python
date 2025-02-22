# tests/resources/activity/test_delete_activity_log.py

"""Tests for the delete_activity_log endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock


def test_delete_activity_log(activity_resource):
    """Test deleting activity log"""
    activity_resource._make_request = Mock()
    activity_resource.delete_activity_log("123")
    activity_resource._make_request.assert_called_once_with(
        "activities/123.json", user_id="-", http_method="DELETE", debug=False
    )
