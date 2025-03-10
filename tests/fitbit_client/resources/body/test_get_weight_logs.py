# tests/fitbit_client/resources/body/test_get_weight_logs.py

"""Tests for the get_weight_logs endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_get_weight_logs(body_resource, mock_oauth_session, mock_response_factory):
    """Test getting weight logs for a date"""
    mock_response = mock_response_factory(
        200,
        {
            "weight": [
                {
                    "bmi": 25.91,
                    "date": "2024-02-10",
                    "logId": 1553067494000,
                    "source": "api",
                    "time": "07:38:14",
                    "weight": 200,
                }
            ]
        },
    )
    mock_oauth_session.request.return_value = mock_response
    result = body_resource.get_weight_logs("2024-02-10")
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/body/log/weight/date/2024-02-10.json",
        data=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        json=None,
        params=None,
    )
    assert len(result["weight"]) == 1
    assert result["weight"][0]["logId"] == 1553067494000


def test_get_weight_logs_validates_date(body_resource):
    """Test that get_weight_logs validates date format"""
    with raises(InvalidDateException) as exc_info:
        body_resource.get_weight_logs("invalid-date")
    assert exc_info.value.field_name == "date"
    assert "Invalid date format" in str(exc_info.value)


def test_custom_user_id(body_resource, mock_oauth_session, mock_response_factory):
    """Test using a custom user ID instead of the default '-'"""
    mock_response = mock_response_factory(200, {"weight": []})
    mock_oauth_session.request.return_value = mock_response
    body_resource.get_weight_logs("2024-02-10", user_id="123ABC")
    mock_oauth_session.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/123ABC/body/log/weight/date/2024-02-10.json",
        data=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        json=None,
        params=None,
    )
