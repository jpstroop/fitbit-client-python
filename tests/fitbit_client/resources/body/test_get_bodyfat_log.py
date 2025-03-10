# tests/fitbit_client/resources/body/test_get_bodyfat_log.py

"""Tests for the get_bodyfat_log endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_get_bodyfat_log(body_resource, mock_oauth_session, mock_response_factory):
    """Test getting body fat logs for a date"""
    mock_response = mock_response_factory(
        200,
        {
            "fat": [
                {
                    "date": "2024-02-10",
                    "fat": 15,
                    "logId": 1553067000000,
                    "source": "api",
                    "time": "07:38:14",
                }
            ]
        },
    )
    mock_oauth_session.request.return_value = mock_response
    result = body_resource.get_bodyfat_log("2024-02-10")
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/body/log/fat/date/2024-02-10.json",
        data=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        json=None,
        params=None,
    )
    assert len(result["fat"]) == 1
    assert result["fat"][0]["logId"] == 1553067000000


def test_get_bodyfat_log_validates_date(body_resource):
    """Test that get_bodyfat_log validates date format"""
    with raises(InvalidDateException) as exc_info:
        body_resource.get_bodyfat_log("invalid-date")
    assert exc_info.value.field_name == "date"
    assert "Invalid date format" in str(exc_info.value)
