# fitbit_client/client/fitbit_client.py

# Standard library imports
from logging import getLogger
from urllib.parse import urlparse

# Local imports
from fitbit_client.auth.oauth import FitbitOAuth2
from fitbit_client.client.resource_methods_mixin import ClientMethodsMixin
from fitbit_client.resources.activezone import ActiveZoneResource
from fitbit_client.resources.activity import ActivityResource
from fitbit_client.resources.activity_timeseries import ActivityTimeSeriesResource
from fitbit_client.resources.body import BodyResource
from fitbit_client.resources.body_timeseries import BodyTimeSeriesResource
from fitbit_client.resources.breathingrate import BreathingRateResource
from fitbit_client.resources.cardio_fitness import CardioFitnessResource
from fitbit_client.resources.device import DeviceResource
from fitbit_client.resources.ecg import ECGResource
from fitbit_client.resources.friends import FriendsResource
from fitbit_client.resources.heartrate_timeseries import HeartRateTimeSeriesResource
from fitbit_client.resources.heartrate_variability import HeartRateVariabilityResource
from fitbit_client.resources.irregular_rhythm import IrregularRhythmResource
from fitbit_client.resources.nutrition import NutritionResource
from fitbit_client.resources.nutrition_timeseries import NutritionTimeSeriesResource
from fitbit_client.resources.sleep import SleepResource
from fitbit_client.resources.spo2 import SpO2Resource
from fitbit_client.resources.subscription import SubscriptionResource
from fitbit_client.resources.temperature import TemperatureResource
from fitbit_client.resources.user import UserResource


class FitbitClient(ClientMethodsMixin):
    """Main client for interacting with Fitbit API"""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        use_callback_server: bool = True,
        token_cache_path: str = "/tmp/fitbit_tokens.json",
        language: str = "en_US",
        locale: str = "en_US",
    ) -> None:
        """Initialize Fitbit client

        Args:
            client_id: Your Fitbit API client ID
            client_secret: Your Fitbit API client secret
            redirect_uri: Complete OAuth redirect URI (e.g. "https://localhost:8080")
            use_callback_server: Whether to use local callback server
            token_cache_path: Path to file where auth tokens should be stored (default: /tmp/fitbit_tokens.json)
            language: Language for API responses
            locale: Locale for API responses
        """
        self.logger = getLogger("fitbit_client")
        self.logger.debug("Initializing Fitbit client")

        self.redirect_uri: str = redirect_uri
        parsed_uri = urlparse(redirect_uri)
        self.logger.debug(
            f"Using redirect URI: {redirect_uri} on {parsed_uri.hostname}:{parsed_uri.port}"
        )

        self.logger.debug("Initializing OAuth handler")
        self.auth: FitbitOAuth2 = FitbitOAuth2(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            token_cache_path=token_cache_path,
            use_callback_server=use_callback_server,
        )

        self.logger.debug(f"Initializing API resources with language={language}, locale={locale}")

    # API aliases will be re-implemented after resource methods have been refactored.

    def authenticate(self, force_new: bool = False) -> bool:
        """
        Authenticate with Fitbit API

        Args:
            force_new: Force new authentication even if valid token exists

        Returns:
            bool: True if authenticated successfully
        """
        self.logger.debug(f"Starting authentication (force_new={force_new})")
        try:
            result = self.auth.authenticate(force_new=force_new)
            self.logger.info("Authentication successful")
            return result
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise
