# tests/resources/electrocardiogram/test_get_ecg_log_list.py

"""Tests for the get_ecg_log_list endpoint."""

# Standard library imports
from unittest.mock import patch

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import PaginationException
from fitbit_client.resources.constants import SortDirection


def test_get_ecg_log_list_success(ecg_resource, mock_oauth_session, mock_response_factory):
    """Test successful retrieval of ECG log list"""
    expected_response = {
        "alerts": [
            {
                "alertTime": "2022-09-28T17:12:30.000",
                "detectedTime": "2022-09-28T17:45:00.000",
                "serviceVersion": "2.2",
                "algoVersion": "1.6",
                "deviceType": "Sense",
            }
        ],
        "pagination": {"afterDate": "2022-09-28T20:00:00", "sort": "asc", "limit": 1, "offset": 0},
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response
    result = ecg_resource.get_ecg_log_list(after_date="2022-09-28", sort=SortDirection.ASCENDING)
    assert result == expected_response
    mock_oauth_session.request.assert_called_once()
    call_args = mock_oauth_session.request.call_args
    assert call_args[0][0] == "GET"
    assert call_args[0][1].endswith("/1/user/-/ecg/list.json")
    assert call_args[1]["params"]["afterDate"] == "2022-09-28"
    assert call_args[1]["params"]["sort"] == "asc"


def test_get_ecg_log_list_with_invalid_date(ecg_resource):
    """Test that invalid date format raises InvalidDateException"""
    with raises(InvalidDateException):
        ecg_resource.get_ecg_log_list(before_date="invalid-date", sort=SortDirection.DESCENDING)
    with raises(InvalidDateException):
        ecg_resource.get_ecg_log_list(after_date="invalid-date", sort=SortDirection.ASCENDING)


def test_get_ecg_log_list_missing_dates(ecg_resource):
    """Test that omitting both before_date and after_date raises PaginationException"""
    with raises(PaginationException) as exc_info:
        ecg_resource.get_ecg_log_list(sort=SortDirection.ASCENDING)
    assert "Either before_date or after_date must be specified" in str(exc_info.value)


def test_get_ecg_log_list_mismatched_sort_direction(ecg_resource):
    """Test validation of sort direction matching date parameter"""
    with raises(PaginationException) as exc_info:
        ecg_resource.get_ecg_log_list(before_date="2022-09-28", sort=SortDirection.ASCENDING)
    assert "Must use sort=DESCENDING with before_date" in str(exc_info.value)

    with raises(PaginationException) as exc_info:
        ecg_resource.get_ecg_log_list(after_date="2022-09-28", sort=SortDirection.DESCENDING)
    assert "Must use sort=ASCENDING with after_date" in str(exc_info.value)


def test_get_ecg_log_list_today(ecg_resource, mock_oauth_session, mock_response_factory):
    """Test that 'today' is accepted as a valid date"""
    mock_response = mock_response_factory(200, {"alerts": []})
    mock_oauth_session.request.return_value = mock_response
    ecg_resource.get_ecg_log_list(before_date="today", sort=SortDirection.DESCENDING)


def test_get_ecg_log_list_invalid_offset(ecg_resource):
    """Test that non-zero offset raises PaginationException"""
    with raises(PaginationException) as exc_info:
        ecg_resource.get_ecg_log_list(
            after_date="2022-09-28", sort=SortDirection.ASCENDING, offset=1
        )
    assert "Only offset=0 is supported" in str(exc_info.value)
    assert exc_info.value.field_name == "offset"


def test_get_ecg_log_list_invalid_limit(ecg_resource):
    """Test that limit > 10 raises PaginationException"""
    with raises(PaginationException) as exc_info:
        ecg_resource.get_ecg_log_list(
            after_date="2022-09-28", sort=SortDirection.ASCENDING, limit=11
        )
    assert "Maximum limit is 10" in str(exc_info.value)
    assert exc_info.value.field_name == "limit"


def test_get_ecg_log_list_creates_iterator(ecg_resource, mock_oauth_session, mock_response_factory):
    """Test that get_ecg_log_list properly creates a paginated iterator"""
    # Create a simplified response with pagination - no need for next URL
    simple_response = {"ecgRecordings": [{"id": "1234567890"}], "pagination": {}}

    # Mock a single response
    mock_response = mock_response_factory(200, simple_response)
    mock_oauth_session.request.return_value = mock_response

    # Get the iterator - but don't consume it yet
    result = ecg_resource.get_ecg_log_list(
        before_date="2024-02-14", sort=SortDirection.DESCENDING, limit=1, as_iterator=True
    )

    # Just verify the type is PaginatedIterator
    # Local imports
    from fitbit_client.resources.pagination import PaginatedIterator

    assert isinstance(result, PaginatedIterator)

    # Check that the initial API call was made, but don't iterate
    assert mock_oauth_session.request.call_count == 1


def test_ecg_log_list_pagination_attributes(
    ecg_resource, mock_oauth_session, mock_response_factory
):
    """Test that the iterator has the right pagination attributes but don't attempt iteration"""
    # Create a response with pagination
    sample_response = {
        "ecgRecordings": [{"id": f"id{i}"} for i in range(3)],
        "pagination": {"offset": 0, "limit": 5},
    }

    # Mock the response
    mock_response = mock_response_factory(200, sample_response)
    mock_oauth_session.request.return_value = mock_response

    # Get iterator but don't iterate
    iterator = ecg_resource.get_ecg_log_list(
        before_date="2024-02-14", sort=SortDirection.DESCENDING, limit=5, as_iterator=True
    )

    # Verify iterator properties
    assert iterator.initial_response == sample_response

    # Check that the API call was made correctly
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/ecg/list.json",
        data=None,
        json=None,
        params={"sort": "desc", "limit": 5, "offset": 0, "beforeDate": "2024-02-14"},
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


@patch("fitbit_client.resources.base.BaseResource._make_request")
def test_get_ecg_log_list_with_debug(mock_make_request, ecg_resource):
    """Test that debug mode returns None from get_ecg_log_list."""
    # Mock _make_request to return None when debug=True
    mock_make_request.return_value = None

    result = ecg_resource.get_ecg_log_list(
        before_date="2023-01-01", sort=SortDirection.DESCENDING, debug=True
    )

    assert result is None
    mock_make_request.assert_called_once_with(
        "ecg/list.json",
        params={"sort": "desc", "limit": 10, "offset": 0, "beforeDate": "2023-01-01"},
        user_id="-",
        debug=True,
    )
