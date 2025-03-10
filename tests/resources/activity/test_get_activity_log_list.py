# tests/resources/activity/test_get_activity_log_list.py

"""Tests for the get_activity_log_list endpoint."""

# Standard library imports
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

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


def test_get_activity_log_list_creates_iterator(
    activity_resource, mock_oauth_session, mock_response_factory
):
    """Test that get_activity_log_list properly creates a paginated iterator"""
    # Create a simplified response with pagination - no next URL needed since we ignore it
    simple_response = {"activities": [{"logId": 1}], "pagination": {}}

    # Mock a single response
    mock_response = mock_response_factory(200, simple_response)
    mock_oauth_session.request.return_value = mock_response

    # Get the iterator - but don't consume it yet
    result = activity_resource.get_activity_log_list(
        before_date="2024-02-13", sort=SortDirection.DESCENDING, as_iterator=True
    )

    # Just verify the type is PaginatedIterator
    # Local imports
    from fitbit_client.resources.pagination import PaginatedIterator

    assert isinstance(result, PaginatedIterator)

    # Check that the initial API call was made, but don't iterate
    assert mock_oauth_session.request.call_count == 1


def test_activity_log_list_pagination_attributes(
    activity_resource, mock_oauth_session, mock_response_factory
):
    """Test that the iterator has the right pagination attributes but don't attempt iteration"""
    # Create a response with pagination
    sample_response = {
        "activities": [{"logId": i} for i in range(5)],
        "pagination": {"offset": 0, "limit": 10},
    }

    # Mock the response
    mock_response = mock_response_factory(200, sample_response)
    mock_oauth_session.request.return_value = mock_response

    # Get iterator but don't iterate
    iterator = activity_resource.get_activity_log_list(
        before_date="2024-02-13", sort=SortDirection.DESCENDING, limit=10, as_iterator=True
    )

    # Verify iterator properties
    assert iterator.initial_response == sample_response

    # Check that the API call was made correctly
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/list.json",
        data=None,
        json=None,
        params={"sort": "desc", "limit": 10, "offset": 0, "beforeDate": "2024-02-13"},
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


@patch("fitbit_client.resources.base.BaseResource._make_request")
def test_get_activity_log_list_with_debug(mock_make_request, activity_resource):
    """Test that debug mode returns None from get_activity_log_list."""
    # Mock _make_request to return None when debug=True
    mock_make_request.return_value = None

    result = activity_resource.get_activity_log_list(
        before_date="2023-01-01", sort=SortDirection.DESCENDING, debug=True
    )

    assert result is None
    mock_make_request.assert_called_once_with(
        "activities/list.json",
        params={"sort": "desc", "limit": 100, "offset": 0, "beforeDate": "2023-01-01"},
        user_id="-",
        debug=True,
    )
