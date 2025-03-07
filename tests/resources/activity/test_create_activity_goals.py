# tests/resources/activity/test_create_activity_goals.py

"""Tests for the create_activity_goals endpoint."""

# Standard library imports
from unittest.mock import Mock

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import ValidationException
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


def test_create_activity_goals_negative_value(activity_resource):
    """Test that negative value raises ValidationException"""
    with raises(ValidationException) as exc_info:
        activity_resource.create_activity_goals(
            period=ActivityGoalPeriod.DAILY, type=ActivityGoalType.STEPS, value=-100
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.error_type == "validation"
    assert exc_info.value.field_name == "value"
    assert "Goal value must be positive" in str(exc_info.value)


def test_create_activity_goals_zero_value(activity_resource):
    """Test that zero value raises ValidationException"""
    with raises(ValidationException) as exc_info:
        activity_resource.create_activity_goals(
            period=ActivityGoalPeriod.DAILY, type=ActivityGoalType.STEPS, value=0
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.error_type == "validation"
    assert exc_info.value.field_name == "value"
    assert "Goal value must be positive" in str(exc_info.value)
