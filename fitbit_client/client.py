# fitbit_client/client.py

# Standard library imports
from logging import getLogger
from urllib.parse import urlparse

# fmt: off
# isort: off
# Auth imports
from fitbit_client.auth.oauth import FitbitOAuth2
from fitbit_client.exceptions import ExpiredTokenException
from fitbit_client.exceptions import InvalidClientException
from fitbit_client.exceptions import InvalidGrantException
from fitbit_client.exceptions import InvalidRequestException
from fitbit_client.exceptions import InvalidTokenException
from fitbit_client.exceptions import OAuthException
from fitbit_client.exceptions import SystemException

# Resource imports
from fitbit_client.resources.active_zone_minutes import ActiveZoneMinutesResource
from fitbit_client.resources.activity import ActivityResource
from fitbit_client.resources.activity_timeseries import ActivityTimeSeriesResource
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


class FitbitClient:
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
        # Initialize API resources
        # fmt: off
        # isort: off
        self.active_zone_minutes: ActiveZoneMinutesResource = ActiveZoneMinutesResource(self.auth.session, language=language, locale=locale)
        self.activity_timeseries: ActivityTimeSeriesResource = ActivityTimeSeriesResource(self.auth.session, language=language, locale=locale)
        self.activity: ActivityResource = ActivityResource(self.auth.session, language=language, locale=locale)
        self.body_timeseries: BodyTimeSeriesResource = BodyTimeSeriesResource(self.auth.session, language=language, locale=locale)
        self.body: BodyResource = BodyResource(self.auth.session, language=language, locale=locale)
        self.breathing_rate: BreathingRateResource = BreathingRateResource(self.auth.session, language=language, locale=locale)
        self.cardio_fitness_score: CardioFitnessScoreResource = CardioFitnessScoreResource(self.auth.session, language=language, locale=locale)
        self.device: DeviceResource = DeviceResource(self.auth.session, language=language, locale=locale)
        self.electrocardiogram: ElectrocardiogramResource = ElectrocardiogramResource(self.auth.session, language=language, locale=locale)
        self.friends: FriendsResource = FriendsResource(self.auth.session, language=language, locale=locale)
        self.heartrate_timeseries: HeartrateTimeSeriesResource = HeartrateTimeSeriesResource(self.auth.session, language=language, locale=locale)
        self.heartrate_variability: HeartrateVariabilityResource = HeartrateVariabilityResource(self.auth.session, language=language, locale=locale)
        self.intraday: IntradayResource = IntradayResource(self.auth.session, language=language, locale=locale)
        self.irregular_rhythm_notifications: IrregularRhythmNotificationsResource = IrregularRhythmNotificationsResource(self.auth.session, language=language, locale=locale)
        self.nutrition_timeseries: NutritionTimeSeriesResource = NutritionTimeSeriesResource(self.auth.session, language=language, locale=locale)
        self.nutrition: NutritionResource = NutritionResource(self.auth.session, language=language, locale=locale)
        self.sleep: SleepResource = SleepResource(self.auth.session, language=language, locale=locale)
        self.spo2: SpO2Resource = SpO2Resource(self.auth.session, language=language, locale=locale)
        self.subscription: SubscriptionResource = SubscriptionResource(self.auth.session, language=language, locale=locale)
        self.temperature: TemperatureResource = TemperatureResource(self.auth.session, language=language, locale=locale)
        self.user: UserResource = UserResource(self.auth.session, language=language, locale=locale)
        # fmt: on
        # isort: on
        self.logger.debug("Fitbit client initialized successfully")

    # API aliases will be re-implemented after resource methods have been refactored.

    def authenticate(self, force_new: bool = False) -> bool:
        """
        Authenticate with Fitbit API

        Args:
            force_new: Force new authentication even if valid token exists

        Returns:
            bool: True if authenticated successfully

        Raises:
            OAuthException: Base class for all OAuth-related exceptions
            ExpiredTokenException: If the OAuth token has expired
            InvalidClientException: If the client_id is invalid
            InvalidGrantException: If the grant_type is invalid
            InvalidTokenException: If the OAuth token is invalid
            InvalidRequestException: If the request syntax is invalid
            SystemException: If there's a system-level failure during authentication
        """
        self.logger.debug(f"Starting authentication (force_new={force_new})")
        try:
            result = self.auth.authenticate(force_new=force_new)
            self.logger.debug("Authentication successful")
            return result
        except OAuthException as e:
            self.logger.error(f"Authentication failed: {e.__class__.__name__}: {str(e)}")
            raise
        except SystemException as e:
            self.logger.error(f"System error during authentication: {str(e)}")
            raise
