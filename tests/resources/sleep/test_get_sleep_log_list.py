# tests/resources/sleep/test_get_sleep_log_list.py

"""Tests for the get_sleep_log_list endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_get_sleep_log_list_success(sleep_resource, mock_oauth_session, mock_response_factory):
    """Test successful retrieval of sleep log list"""
    expected_response = {
        "sleep": [{"dateOfSleep": "2024-02-13"}],
        "pagination": {"next": "", "previous": ""},
    }
    mock_response = mock_response_factory(200, expected_response)
    mock_oauth_session.request.return_value = mock_response
    result = sleep_resource.get_sleep_log_list(before_date="2024-02-13")
    assert result == expected_response
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1.2/user/-/sleep/list.json",
        data=None,
        json=None,
        params={"sort": "desc", "limit": 100, "offset": 0, "beforeDate": "2024-02-13"},
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )


def test_get_sleep_log_list_missing_dates(sleep_resource):
    """Test that omitting both dates raises ValueError"""
    with raises(ValueError) as exc_info:
        sleep_resource.get_sleep_log_list()
    assert "Must specify either before_date or after_date" in str(exc_info.value)


def test_get_sleep_log_list_mismatched_sort_direction(sleep_resource):
    """Test validation of sort direction matching date parameter"""
    with raises(ValueError) as exc_info:
        sleep_resource.get_sleep_log_list(before_date="2024-02-13", sort="asc")
    assert "Must use sort='desc' with before_date" in str(exc_info.value)
    with raises(ValueError) as exc_info:
        sleep_resource.get_sleep_log_list(after_date="2024-02-13", sort="desc")
    assert "Must use sort='asc' with after_date" in str(exc_info.value)


def test_get_sleep_log_list_invalid_dates(sleep_resource):
    """Test that invalid date formats raise InvalidDateException"""
    with raises(InvalidDateException):
        sleep_resource.get_sleep_log_list(before_date="invalid")
    with raises(InvalidDateException):
        sleep_resource.get_sleep_log_list(after_date="invalid")


def test_get_sleep_log_list_invalid_limit(sleep_resource):
    """Test that exceeding max limit raises ValueError"""
    with raises(ValueError) as exc_info:
        sleep_resource.get_sleep_log_list(before_date="2024-02-13", limit=101)
    assert "Maximum limit is 100" in str(exc_info.value)


def test_get_sleep_log_list_invalid_sort(sleep_resource):
    """Test that invalid sort value raises ValueError"""
    with raises(ValueError) as exc_info:
        sleep_resource.get_sleep_log_list(before_date="2024-02-13", sort="invalid")
    assert "Sort must be either 'asc' or 'desc'" in str(exc_info.value)


def test_get_sleep_log_list_allows_today(sleep_resource, mock_oauth_session, mock_response_factory):
    """Test that 'today' is accepted for date parameters"""
    mock_response = mock_response_factory(200, {"sleep": []})
    mock_oauth_session.request.return_value = mock_response
    sleep_resource.get_sleep_log_list(before_date="today", sort="desc")
    sleep_resource.get_sleep_log_list(after_date="today", sort="asc")
