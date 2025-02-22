# tests/resources/body/test_create_weight_log.py

"""Tests for the create_weight_log endpoint."""

# Third party imports

# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import InvalidDateException


def test_create_weight_log_with_time(body_resource, mock_oauth_session, mock_response_factory):
    """Test creating a weight log entry with time parameter"""
    mock_response = mock_response_factory(
        201,
        {
            "weightLog": {
                "bmi": 25.91,
                "date": "2024-02-10",
                "logId": 1553067494000,
                "source": "api",
                "time": "07:38:14",
                "weight": 200,
            }
        },
    )
    mock_oauth_session.request.return_value = mock_response
    result = body_resource.create_weight_log(weight=200, date="2024-02-10", time="07:38:14")
    mock_oauth_session.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/body/log/weight.json",
        data=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        json=None,
        params={"weight": 200, "date": "2024-02-10", "time": "07:38:14"},
    )
    assert result["weightLog"]["logId"] == 1553067494000


def test_create_weight_log_without_time(body_resource, mock_oauth_session, mock_response_factory):
    """Test creating a weight log entry without time parameter"""
    mock_response = mock_response_factory(
        201,
        {
            "weightLog": {
                "bmi": 25.91,
                "date": "2024-02-10",
                "logId": 1553067494000,
                "source": "api",
                "time": "23:59:59",
                "weight": 200,
            }
        },
    )
    mock_oauth_session.request.return_value = mock_response
    result = body_resource.create_weight_log(weight=200, date="2024-02-10")
    mock_oauth_session.request.assert_called_once_with(
        "POST",
        "https://api.fitbit.com/1/user/-/body/log/weight.json",
        data=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
        json=None,
        params={"weight": 200, "date": "2024-02-10"},
    )
    assert result["weightLog"]["logId"] == 1553067494000


def test_debug_mode(body_resource, capsys):
    """Test debug mode outputs curl command"""
    body_resource.oauth.token = {"access_token": "test-token"}
    result = body_resource.create_weight_log(
        weight=200, date="2024-02-10", time="07:38:14", debug=True
    )
    captured = capsys.readouterr()
    assert result is None
    assert "curl" in captured.out
    assert "POST" in captured.out
    assert "/body/log/weight.json" in captured.out
    assert "weight=200" in captured.out
    assert "date=2024-02-10" in captured.out
    assert "time=07%3A38%3A14" in captured.out


def test_create_weight_log_validates_date(body_resource):
    """Test that create_weight_log validates date format"""
    with raises(InvalidDateException) as exc_info:
        body_resource.create_weight_log(weight=200, date="invalid-date")
    assert exc_info.value.field_name == "date"
    assert "Invalid date format" in str(exc_info.value)
