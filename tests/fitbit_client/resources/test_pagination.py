# tests/fitbit_client/resources/test_pagination.py

"""Tests for the Pagination module."""

# Standard library imports
import sys
import typing
from typing import Any
from typing import Dict
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture

# Local imports
from fitbit_client.resources.pagination import PaginatedIterator
from fitbit_client.resources.pagination import create_paginated_iterator
from fitbit_client.utils.types import JSONDict


@fixture
def mock_resource() -> Mock:
    """Mock resource with _make_request method"""
    resource = Mock()
    resource._make_request.return_value = {}
    return resource


@fixture
def sample_pagination_response() -> JSONDict:
    """Sample response with pagination"""
    return {
        "activities": [{"logId": 1, "name": "Activity 1"}, {"logId": 2, "name": "Activity 2"}],
        "pagination": {
            "next": (
                "https://api.fitbit.com/1/user/-/activities/list.json?offset=2&limit=2&sort=desc&beforeDate=2025-03-09"
            ),
            "previous": None,
            "limit": 2,
            "offset": 0,
        },
    }


@fixture
def sample_pagination_next_response() -> JSONDict:
    """Sample response for the next page"""
    return {
        "activities": [{"logId": 3, "name": "Activity 3"}, {"logId": 4, "name": "Activity 4"}],
        "pagination": {
            "next": None,
            "previous": (
                "https://api.fitbit.com/1/user/-/activities/list.json?offset=0&limit=2&sort=desc&beforeDate=2025-03-09"
            ),
            "limit": 2,
            "offset": 2,
        },
    }


def test_import_with_type_checking():
    """Test BaseResource import with TYPE_CHECKING enabled"""
    # Store original value
    original_type_checking = typing.TYPE_CHECKING

    try:
        # Override TYPE_CHECKING to True
        typing.TYPE_CHECKING = True

        # Force reload of the module
        if "fitbit_client.resources.pagination" in sys.modules:
            del sys.modules["fitbit_client.resources.pagination"]

        # Now import the module with TYPE_CHECKING as True
        # Local imports
        from fitbit_client.resources.pagination import PaginatedIterator

        # This should have imported BaseResource due to TYPE_CHECKING being True
        assert "fitbit_client.resources.base" in sys.modules

    finally:
        # Restore TYPE_CHECKING to its original value
        typing.TYPE_CHECKING = original_type_checking


def test_create_paginated_iterator(mock_resource, sample_pagination_response):
    """Test creating a paginated iterator from a response"""
    endpoint = "activities/list.json"
    method_params = {"beforeDate": "2025-03-09", "sort": "desc", "limit": 2, "offset": 0}

    iterator = create_paginated_iterator(
        response=sample_pagination_response,
        resource=mock_resource,
        endpoint=endpoint,
        method_params=method_params,
    )

    assert isinstance(iterator, PaginatedIterator)
    assert iterator.initial_response == sample_pagination_response


def test_data_key_detection(mock_resource):
    """Test that the data key is correctly detected for different response types"""
    # Test activities data key
    activity_response = {"activities": [{"logId": 1}]}
    activity_iterator = PaginatedIterator(
        response=activity_response,
        endpoint="activities/list.json",
        method_params={},
        fetch_next_page=Mock(),
    )
    assert activity_iterator._data_key == "activities"

    # Test sleep data key
    sleep_response = {"sleep": [{"logId": 1}]}
    sleep_iterator = PaginatedIterator(
        response=sleep_response,
        endpoint="sleep/list.json",
        method_params={},
        fetch_next_page=Mock(),
    )
    assert sleep_iterator._data_key == "sleep"

    # Test ecg data key
    ecg_response = {"ecgReadings": [{"ecgReadingId": 1}]}
    ecg_iterator = PaginatedIterator(
        response=ecg_response, endpoint="ecg/list.json", method_params={}, fetch_next_page=Mock()
    )
    assert ecg_iterator._data_key == "ecgReadings"

    # Test alerts data key
    irn_response = {"alerts": [{"alertId": 1}]}
    irn_iterator = PaginatedIterator(
        response=irn_response, endpoint="irn/alerts.json", method_params={}, fetch_next_page=Mock()
    )
    assert irn_iterator._data_key == "alerts"

    # Test unknown data key (should return None)
    unknown_response = {"unknown_key": [{"id": 1}]}
    unknown_iterator = PaginatedIterator(
        response=unknown_response, endpoint="unknown.json", method_params={}, fetch_next_page=Mock()
    )
    assert unknown_iterator._data_key is None


def test_next_params_extraction():
    """Test extraction of parameters from next URL"""
    iterator = PaginatedIterator(
        response={
            "activities": [],
            "pagination": {
                "next": (
                    "https://api.fitbit.com/1/user/-/activities/list.json?offset=2&limit=2&sort=desc&beforeDate=2025-03-09"
                )
            },
        },
        endpoint="activities/list.json",
        method_params={},
        fetch_next_page=Mock(),
    )

    next_params = iterator._get_next_params()
    assert next_params is not None
    assert next_params["offset"] == "2"
    assert next_params["limit"] == "2"
    assert next_params["sort"] == "desc"
    assert next_params["beforeDate"] == "2025-03-09"

    # Test with no next URL
    iterator._last_page = {"pagination": {"next": None}}
    assert iterator._get_next_params() is None

    # Test with pagination not a dict
    iterator._last_page = {"pagination": "not-a-dict"}
    assert iterator._get_next_params() is None

    # Test with next URL not a string
    iterator._last_page = {"pagination": {"next": 123}}
    assert iterator._get_next_params() is None


def test_full_pagination(
    mock_resource, sample_pagination_response, sample_pagination_next_response
):
    """Test full iteration through all pages"""
    endpoint = "activities/list.json"
    method_params = {"beforeDate": "2025-03-09", "sort": "desc", "limit": 2, "offset": 0}

    fetch_next_page = Mock(return_value=sample_pagination_next_response)

    iterator = PaginatedIterator(
        response=sample_pagination_response,
        endpoint=endpoint,
        method_params=method_params,
        fetch_next_page=fetch_next_page,
    )

    # Collect all pages
    pages = list(iterator)

    # Should have 2 pages
    assert len(pages) == 2
    assert pages[0] == sample_pagination_response
    assert pages[1] == sample_pagination_next_response

    # fetch_next_page should be called once with extracted params
    fetch_next_page.assert_called_once_with(
        endpoint, {"offset": "2", "limit": "2", "sort": "desc", "beforeDate": "2025-03-09"}
    )


def test_error_handling(mock_resource, sample_pagination_response):
    """Test error handling in the pagination iterator"""
    endpoint = "activities/list.json"
    method_params = {"beforeDate": "2025-03-09", "sort": "desc", "limit": 2, "offset": 0}

    # Test with non-dict response
    fetch_next_page_invalid = Mock(return_value="not a dict")
    invalid_iterator = PaginatedIterator(
        response=sample_pagination_response,
        endpoint=endpoint,
        method_params=method_params,
        fetch_next_page=fetch_next_page_invalid,
    )

    # Should only get initial page
    pages = list(invalid_iterator)
    assert len(pages) == 1

    # Test with exception
    fetch_next_page_error = Mock(side_effect=Exception("Test error"))
    error_iterator = PaginatedIterator(
        response=sample_pagination_response,
        endpoint=endpoint,
        method_params=method_params,
        fetch_next_page=fetch_next_page_error,
    )

    # Should only get initial page
    pages = list(error_iterator)
    assert len(pages) == 1


def test_fetch_next_page_callback(mock_resource, sample_pagination_response):
    """Test that the fetch_next_page callback correctly uses the resource"""
    endpoint = "activities/list.json"
    method_params = {"beforeDate": "2025-03-09", "sort": "desc", "limit": 2, "offset": 0}

    # Set up mock_resource to return the next page
    mock_resource._make_request.return_value = {"activities": [{"logId": 3}], "pagination": {}}

    # Create iterator with debug=True to test that parameter
    iterator = create_paginated_iterator(
        response=sample_pagination_response,
        resource=mock_resource,
        endpoint=endpoint,
        method_params=method_params,
        debug=True,
    )

    # Manually call next iteration to trigger fetch_next_page
    _ = next(iterator)  # Initial page
    try:
        _ = next(iterator)  # Next page
    except StopIteration:
        pass  # Expected if there's no next URL

    # Verify resource's _make_request was called with debug=True
    mock_resource._make_request.assert_called_with(
        endpoint=endpoint,
        params={"offset": "2", "limit": "2", "sort": "desc", "beforeDate": "2025-03-09"},
        debug=True,
    )


def test_create_paginated_iterator_adds_pagination_if_missing(mock_resource):
    """Test that create_paginated_iterator adds a pagination object if it's missing"""
    response = {"activities": [{"logId": 1}]}
    endpoint = "activities/list.json"
    method_params = {"beforeDate": "2025-03-09", "sort": "desc", "limit": 2, "offset": 0}

    iterator = create_paginated_iterator(
        response=response, resource=mock_resource, endpoint=endpoint, method_params=method_params
    )

    # Verify a pagination object was added
    assert "pagination" in iterator.initial_response
    assert iterator.initial_response["pagination"] == {}


def test_fetch_next_page_non_dict_result():
    """Test handling of non-dict results in fetch_next_page"""
    # Set up a resource that returns a non-dict response
    resource = Mock()
    resource._make_request.return_value = "not a dict"

    response = {"activities": [{"logId": 1}], "pagination": {"next": "test-url"}}

    # Create iterator
    iterator = create_paginated_iterator(
        response=response, resource=resource, endpoint="test.json", method_params={}
    )

    # Call fetch_next_page to test non-dict handling
    result = iterator._fetch_next_page("test.json", {"param": "value"})

    # Should return empty dict for non-dict responses
    assert result == {}


def test_fetch_next_page_add_pagination():
    """Test that fetch_next_page adds a pagination section when missing"""
    # Set up a resource that returns a response without pagination
    resource = Mock()
    resource._make_request.return_value = {"activities": [{"logId": 1}]}  # No pagination

    response = {"activities": [{"logId": 1}], "pagination": {"next": "test-url"}}

    # Create iterator
    iterator = create_paginated_iterator(
        response=response, resource=resource, endpoint="test.json", method_params={}
    )

    # Call fetch_next_page and verify it adds pagination
    result = iterator._fetch_next_page("test.json", {"param": "value"})

    # Should add an empty pagination object
    assert "pagination" in result
    assert result["pagination"] == {}


def test_fetch_next_page_exception_handling():
    """Test that fetch_next_page handles exceptions properly"""
    # Set up a resource that raises an exception
    resource = Mock()
    resource._make_request.side_effect = Exception("Test exception")

    response = {"activities": [{"logId": 1}], "pagination": {"next": "test-url"}}

    # Create iterator
    iterator = create_paginated_iterator(
        response=response, resource=resource, endpoint="test.json", method_params={}
    )

    # Call fetch_next_page and verify it handles the exception
    result = iterator._fetch_next_page("test.json", {"param": "value"})

    # Should return an empty dict on exception
    assert result == {}
