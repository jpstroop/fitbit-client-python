# tests/conftest.py

# Standard library imports
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
from pytest import fixture
from requests import Response
from requests_oauthlib import OAuth2Session

# fmt: off
# isort: off
from fitbit_client.resources.active_zone_minutes import ActiveZoneMinutesResource
from fitbit_client.resources.activity import ActivityResource
from fitbit_client.resources.activity_timeseries import ActivityTimeSeriesResource
from fitbit_client.resources._base import BaseResource
from fitbit_client.resources.body import BodyResource
from fitbit_client.resources.body_timeseries import BodyTimeSeriesResource
from fitbit_client.resources.breathing_rate import BreathingRateResource
from fitbit_client.resources.cardio_fitness_score import CardioFitnessScoreResource
from fitbit_client.resources.device import DeviceResource
from fitbit_client.resources.electrocardiogram import ElectrocardiogramResource
from fitbit_client.resources.friends import FriendsResource
from fitbit_client.resources.heartrate_timeseries import HeartrateTimeSeriesResource
from fitbit_client.resources.heartrate_variability import HeartrateVariabilityResource
from fitbit_client.resources.intraday import IntradayResource
from fitbit_client.resources.irregular_rhythm_notifications import IrregularRhythmNotificationsResource
from fitbit_client.resources.nutrition import NutritionResource
from fitbit_client.resources.nutrition_timeseries import NutritionTimeSeriesResource
from fitbit_client.resources.sleep import SleepResource
from fitbit_client.resources.spo2 import SpO2Resource
from fitbit_client.resources.subscription import SubscriptionResource
from fitbit_client.resources.temperature import TemperatureResource
from fitbit_client.resources.user import UserResource
# isort: on
# fmt: on


@fixture
def mock_oauth_session():
    """Fixture to provide a mocked OAuth2Session with standard configuration"""
    session = Mock(spec=OAuth2Session)
    session.request = Mock()
    return session


@fixture
def mock_response():
    """Fixture to provide a mocked requests Response with configurable behavior"""
    response = Mock(spec=Response)
    response.status_code = 200
    response.text = ""
    response.json.return_value = {"success": True}
    response.headers = {"content-type": "application/json"}
    response.raise_for_status.return_value = None
    return response


@fixture
def mock_server():
    """Provide a mock server instance"""
    server = Mock()
    server.last_callback = None
    return server


@fixture
def mock_logger():
    """Fixture to provide a mock logger that's used across resources"""
    return Mock()


@fixture
def mock_response_factory():
    """Factory fixture for creating mock responses with specific attributes"""

    def _create_mock_response(
        status_code, json_data=None, headers=None, content_type="application/json"
    ):
        response = Mock(spec=Response)
        response.status_code = status_code

        # Start with content-type, then add any additional headers
        response.headers = {"content-type": content_type}
        if headers:
            response.headers.update(headers)

        response.text = ""  # Default empty text
        if json_data:
            response.json.return_value = json_data
        else:
            response.json.return_value = {}
        return response

    return _create_mock_response


@fixture
def base_resource(mock_oauth_session, mock_logger):
    """Fixture to provide a BaseResource instance with standard locale settings"""
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        resource = BaseResource(
            oauth_session=mock_oauth_session,
            locale="en_US",
            language="en_US",
            max_retries=3,
            retry_after_seconds=60,
            retry_backoff_factor=1.5,
        )
        return resource


@fixture
def activity_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return ActivityResource(oauth_session=mock_oauth_session, locale="en_US", language="en_US")


@fixture
def activity_timeseries_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return ActivityTimeSeriesResource(
            oauth_session=mock_oauth_session, locale="en_US", language="en_US"
        )


@fixture
def azm_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return ActiveZoneMinutesResource(
            oauth_session=mock_oauth_session, locale="en_US", language="en_US"
        )


@fixture
def body_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return BodyResource(mock_oauth_session, "en_US", "en_US")


@fixture
def body_timeseries(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return BodyTimeSeriesResource(mock_oauth_session, "en_US", "en_US")


@fixture
def breathing_rate_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return BreathingRateResource(mock_oauth_session, "en_US", "en_US")


@fixture
def cardio_fitness_score_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return CardioFitnessScoreResource(mock_oauth_session, "en_US", "en_US")


@fixture
def device_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return DeviceResource(mock_oauth_session, "en_US", "en_US")


@fixture
def ecg_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return ElectrocardiogramResource(mock_oauth_session, "en_US", "en_US")


@fixture
def friends_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return FriendsResource(oauth_session=mock_oauth_session, locale="en_US", language="en_US")


@fixture
def heartrate_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return HeartrateTimeSeriesResource(
            oauth_session=mock_oauth_session, locale="en_US", language="en_US"
        )


@fixture
def hrv_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return HeartrateVariabilityResource(mock_oauth_session, "en_US", "en_US")


@fixture
def intraday_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return IntradayResource(oauth_session=mock_oauth_session, locale="en_US", language="en_US")


@fixture
def irn_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return IrregularRhythmNotificationsResource(mock_oauth_session, "en_US", "en_US")


@fixture
def nutrition_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return NutritionResource(oauth_session=mock_oauth_session, locale="en_US", language="en_US")


@fixture
def nutrition_timeseries_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return NutritionTimeSeriesResource(mock_oauth_session, "en_US", "en_US")


@fixture
def sleep_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return SleepResource(mock_oauth_session, "en_US", "en_US")


@fixture
def spo2_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return SpO2Resource(mock_oauth_session, "en_US", "en_US")


@fixture
def subscription_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return SubscriptionResource(mock_oauth_session, "en_US", "en_US")


@fixture
def temperature_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return TemperatureResource(mock_oauth_session, "en_US", "en_US")


@fixture
def user_resource(mock_oauth_session, mock_logger):
    with patch("fitbit_client.resources._base.getLogger", return_value=mock_logger):
        return UserResource(mock_oauth_session, "en_US", "en_US")
