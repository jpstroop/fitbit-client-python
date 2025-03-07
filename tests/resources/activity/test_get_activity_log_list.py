# tests/resources/activity/test_get_activity_log_list.py

"""Tests for the get_activity_log_list endpoint."""

# Standard library imports
from unittest.mock import Mock

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import PaginationException
from fitbit_client.resources.constants import SortDirection


def test_get_activity_log_list_validates_limit(activity_resource):
    """Test that exceeding max limit raises PaginationException"""
    with raises(PaginationException) as exc_info:
        activity_resource.get_activity_log_list(
            limit=101, before_date="2023-01-01", sort=SortDirection.DESCENDING
        )
    assert "Maximum limit is 100" in str(exc_info.value)
    assert exc_info.value.field_name == "limit"


def test_get_activity_log_list_accepts_valid_limit(activity_resource):
    """Test that valid limit is accepted"""
    activity_resource._make_request = Mock()
    activity_resource.get_activity_log_list(
        limit=100, before_date="2023-01-01", sort=SortDirection.DESCENDING
    )
    activity_resource._make_request.assert_called_once()

    activity_resource._make_request = Mock()
    activity_resource.get_activity_log_list(
        limit=50, before_date="2023-01-01", sort=SortDirection.DESCENDING
    )
    activity_resource._make_request.assert_called_once()


def test_get_activity_log_list_parameters(activity_resource):
    """Test that parameters are correctly passed to request"""
    activity_resource._make_request = Mock()
    activity_resource.get_activity_log_list(
        after_date="2022-12-01", sort=SortDirection.ASCENDING, limit=50, offset=0
    )
    activity_resource._make_request.assert_called_once_with(
        "activities/list.json",
        params={"sort": "asc", "limit": 50, "offset": 0, "afterDate": "2022-12-01"},
        user_id="-",
        debug=False,
    )


def test_get_activity_log_list_accepts_valid_sort(activity_resource):
    """Test that valid sort orders are accepted"""
    activity_resource._make_request = Mock()
    activity_resource.get_activity_log_list(sort=SortDirection.ASCENDING, after_date="2023-01-01")
    activity_resource._make_request.assert_called_once()

    activity_resource._make_request = Mock()
    activity_resource.get_activity_log_list(sort=SortDirection.DESCENDING, before_date="2023-01-01")
    activity_resource._make_request.assert_called_once()


def test_get_activity_log_list_invalid_dates(activity_resource):
    """Test invalid dates in get_activity_log_list"""
    with raises(InvalidDateException) as exc_info:
        activity_resource.get_activity_log_list(
            before_date="invalid-date", sort=SortDirection.DESCENDING
        )
    assert "invalid-date" in str(exc_info.value)
    assert exc_info.value.field_name == "before_date"

    with raises(InvalidDateException) as exc_info:
        activity_resource.get_activity_log_list(
            after_date="invalid-date", sort=SortDirection.ASCENDING
        )
    assert "invalid-date" in str(exc_info.value)
    assert exc_info.value.field_name == "after_date"
