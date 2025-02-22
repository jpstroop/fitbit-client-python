# tests/resources/electrocardiogram/test_get_ecg_log_list.py

"""Tests for the get_ecg_log_list endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


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
    result = ecg_resource.get_ecg_log_list(after_date="2022-09-28", sort="asc")
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
        ecg_resource.get_ecg_log_list(before_date="invalid-date")
    with raises(InvalidDateException):
        ecg_resource.get_ecg_log_list(after_date="invalid-date")


def test_get_ecg_log_list_missing_dates(ecg_resource):
    """Test that omitting both before_date and after_date raises ValueError"""
    with raises(ValueError, match="Either before_date or after_date must be specified"):
        ecg_resource.get_ecg_log_list(sort="asc")


def test_get_ecg_log_list_mismatched_sort_direction(ecg_resource):
    """Test validation of sort direction matching date parameter"""
    with raises(ValueError, match="Must use sort='desc' with before_date"):
        ecg_resource.get_ecg_log_list(before_date="2022-09-28", sort="asc")
    with raises(ValueError, match="Must use sort='asc' with after_date"):
        ecg_resource.get_ecg_log_list(after_date="2022-09-28", sort="desc")


def test_get_ecg_log_list_today(ecg_resource, mock_oauth_session, mock_response_factory):
    """Test that 'today' is accepted as a valid date"""
    mock_response = mock_response_factory(200, {"alerts": []})
    mock_oauth_session.request.return_value = mock_response
    ecg_resource.get_ecg_log_list(before_date="today", sort="desc")


def test_get_ecg_log_list_invalid_offset(ecg_resource):
    """Test that non-zero offset raises ValueError"""
    with raises(ValueError, match="Only offset=0 is supported"):
        ecg_resource.get_ecg_log_list(after_date="2022-09-28", offset=1)


def test_get_ecg_log_list_invalid_limit(ecg_resource):
    """Test that limit > 10 raises ValueError"""
    with raises(ValueError, match="Maximum limit is 10"):
        ecg_resource.get_ecg_log_list(after_date="2022-09-28", limit=11)


def test_get_ecg_log_list_invalid_sort(ecg_resource):
    """Test that invalid sort value raises ValueError"""
    with raises(ValueError, match="Sort must be either 'asc' or 'desc'"):
        ecg_resource.get_ecg_log_list(after_date="2022-09-28", sort="invalid")
