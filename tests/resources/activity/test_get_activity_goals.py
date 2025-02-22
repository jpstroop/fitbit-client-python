# tests/resources/activity/test_get_activity_goals.py

"""Tests for the get_activity_goals endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock

# Local imports
from fitbit_client.resources.constants import ActivityGoalPeriod


def test_get_activity_goals(activity_resource):
    """Test getting activity goals"""
    activity_resource._make_request = Mock()
    activity_resource.get_activity_goals(ActivityGoalPeriod.DAILY)
    activity_resource._make_request.assert_called_once_with(
        "activities/goals/daily.json", user_id="-", debug=False
    )
