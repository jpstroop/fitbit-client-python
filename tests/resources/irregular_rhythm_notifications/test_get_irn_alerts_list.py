# tests/resources/irregular_rhythm_notifications/test_get_irn_alerts_list.py

"""Tests for the get_irn_alerts_list endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_get_irn_alerts_list_success(irn_resource, mock_oauth_session, mock_response_factory):
    """Test successful retrieval of IRN alerts"""
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
    result = irn_resource.get_irn_alerts_list(sort="asc", after_date="2022-09-28")
    assert result == expected_response
    mock_oauth_session.request.assert_called_once()
    call_args = mock_oauth_session.request.call_args
    assert call_args[0][0] == "GET"
    assert call_args[0][1].endswith("/1/user/-/irn/alerts/list.json")
    assert call_args[1]["params"]["afterDate"] == "2022-09-28"
    assert call_args[1]["params"]["sort"] == "asc"


def test_get_irn_alerts_list_today(irn_resource, mock_oauth_session, mock_response_factory):
    """Test that 'today' is accepted as a valid date"""
    mock_response = mock_response_factory(200, {"alerts": []})
    mock_oauth_session.request.return_value = mock_response
    irn_resource.get_irn_alerts_list(sort="asc", after_date="today")
    irn_resource.get_irn_alerts_list(sort="desc", before_date="today")


def test_get_irn_alerts_list_missing_dates(irn_resource):
    """Test that omitting both before_date and after_date raises ValueError"""
    with raises(ValueError, match="Either before_date or after_date must be specified"):
        irn_resource.get_irn_alerts_list(sort="asc")


def test_get_irn_alerts_list_mismatched_sort_direction(irn_resource):
    """Test validation of sort direction matching date parameter"""
    with raises(ValueError, match="Must use after_date with ascending sort"):
        irn_resource.get_irn_alerts_list(sort="asc", before_date="2022-09-28")
    with raises(ValueError, match="Must use before_date with descending sort"):
        irn_resource.get_irn_alerts_list(sort="desc", after_date="2022-09-28")


def test_get_irn_alerts_list_invalid_dates(irn_resource):
    """Test that invalid date formats raise InvalidDateException"""
    with raises(InvalidDateException):
        irn_resource.get_irn_alerts_list(sort="asc", after_date="invalid-date")
    with raises(InvalidDateException):
        irn_resource.get_irn_alerts_list(sort="desc", before_date="invalid-date")


def test_get_irn_alerts_list_invalid_offset(irn_resource):
    """Test that non-zero offset raises ValueError"""
    with raises(ValueError, match="Only offset=0 is supported for IRN alerts pagination"):
        irn_resource.get_irn_alerts_list(sort="asc", offset=1, after_date="2022-09-28")


def test_get_irn_alerts_list_invalid_limit(irn_resource):
    """Test that limit > 10 raises ValueError"""
    with raises(ValueError, match="Maximum limit is 10 entries"):
        irn_resource.get_irn_alerts_list(sort="asc", limit=11, after_date="2022-09-28")


def test_get_irn_alerts_list_invalid_sort(irn_resource):
    """Test that invalid sort value raises ValueError"""
    with raises(ValueError, match="Sort must be either 'asc' or 'desc'"):
        irn_resource.get_irn_alerts_list(sort="invalid", after_date="2022-09-28")
