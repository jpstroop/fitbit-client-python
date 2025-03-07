# tests/resources/body/test_create_bodyfat_log.py

"""Tests for the create_bodyfat_log endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_create_bodyfat_log_with_time(body_resource, mock_oauth_session, mock_response_factory):
    """Test creating a body fat log entry with time parameter"""
    mock_response = mock_response_factory(
        201,
        {
            "fatLog": {
                "date": "2024-02-10",
                "fat": 15,
                "logId": 1553069700000,
                "source": "api",
                "time": "08:15:00",
            }
        },
    )
    mock_oauth_session.request.return_value = mock_response
    result = body_resource.create_bodyfat_log(fat=15.0, date="2024-02-10", time="08:15:00")
    mock_oauth_session.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/body/log/fat.json",
        data=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        json=None,
        params={"fat": 15.0, "date": "2024-02-10", "time": "08:15:00"},
    )
    assert result["fatLog"]["logId"] == 1553069700000


def test_create_bodyfat_log_without_time(body_resource, mock_oauth_session, mock_response_factory):
    """Test creating a body fat log entry without time parameter"""
    mock_response = mock_response_factory(
        201,
        {
            "fatLog": {
                "date": "2024-02-10",
                "fat": 15,
                "logId": 1553069700000,
                "source": "api",
                "time": "23:59:59",
            }
        },
    )
    mock_oauth_session.request.return_value = mock_response
    result = body_resource.create_bodyfat_log(fat=15.0, date="2024-02-10")
    mock_oauth_session.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/body/log/fat.json",
        data=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        json=None,
        params={"fat": 15.0, "date": "2024-02-10"},
    )
    assert result["fatLog"]["logId"] == 1553069700000


def test_create_bodyfat_log_validates_date(body_resource):
    """Test that create_bodyfat_log validates date format"""
    with raises(InvalidDateException) as exc_info:
        body_resource.create_bodyfat_log(fat=15.0, date="invalid-date")
    assert exc_info.value.field_name == "date"
    assert "Invalid date format" in str(exc_info.value)
