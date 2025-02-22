# tests/resources/activity/test_get_activity_tcx.py

"""Tests for the get_activity_tcx endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock


def test_get_activity_tcx(activity_resource):
    """Test getting activity TCX data"""
    activity_resource._make_request = Mock()
    activity_resource.get_activity_tcx(123)
    activity_resource._make_request.assert_called_once_with(
        "activities/123.tcx", params=None, user_id="-", debug=False
    )
    activity_resource._make_request = Mock()
    activity_resource.get_activity_tcx("123", include_partial_tcx=True)
    activity_resource._make_request.assert_called_once_with(
        "activities/123.tcx", params={"includePartialTCX": True}, user_id="-", debug=False
    )
