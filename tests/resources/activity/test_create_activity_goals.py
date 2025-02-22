# tests/resources/activity/test_create_activity_goals.py

"""Tests for the create_activity_goals endpoint."""

# Standard library imports

# Standard library imports
from unittest.mock import Mock

# Local imports
from fitbit_client.resources.constants import ActivityGoalPeriod
from fitbit_client.resources.constants import ActivityGoalType


def test_create_activity_goals(activity_resource):
    """Test creating activity goal"""
    activity_resource._make_request = Mock()
    activity_resource.create_activity_goals(
        period=ActivityGoalPeriod.DAILY, type=ActivityGoalType.STEPS, value=10000
    )
    activity_resource._make_request.assert_called_once_with(
        "activities/goals/daily.json",
        params={"type": "steps", "value": 10000},
        user_id="-",
        http_method="POST",
        debug=False,
    )
