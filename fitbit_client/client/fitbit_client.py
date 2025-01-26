# client/__init__.py
# Standard library imports
from typing import Optional
from urllib.parse import urlparse

# Third party imports
from auth.oauth import FitbitOAuth2
from client.resource_methods_mixin import ClientMethodsMixin
from resources.activezone import ActiveZoneResource
from resources.activity import ActivityResource
from resources.activity_timeseries import ActivityTimeSeriesResource
from resources.body import BodyResource
from resources.body_timeseries import BodyTimeSeriesResource
from resources.breathingrate import BreathingRateResource
from resources.cardio_fitness import CardioFitnessResource
from resources.device import DeviceResource
from resources.ecg import ECGResource
from resources.friends import FriendsResource
from resources.heartrate_timeseries import HeartRateTimeSeriesResource
from resources.heartrate_variability import HeartRateVariabilityResource
from resources.irregular_rhythm import IrregularRhythmResource
from resources.nutrition import NutritionResource
from resources.nutrition_timeseries import NutritionTimeSeriesResource
from resources.sleep import SleepResource
from resources.spo2 import SpO2Resource
from resources.subscription import SubscriptionResource
from resources.temperature import TemperatureResource
from resources.user import UserResource


class FitbitClient(ClientMethodsMixin):
    """Main client for interacting with Fitbit API"""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        use_callback_server: bool = True,
        language: str = "en_US",
        locale: str = "en_US",
    ) -> None:
        """Initialize Fitbit client

        Args:
            client_id: Your Fitbit API client ID
            client_secret: Your Fitbit API client secret
            redirect_uri: Complete OAuth redirect URI (e.g. "https://localhost:8080")
            use_callback_server: Whether to use local callback server
        """
        self.redirect_uri: str = redirect_uri

        self.auth: FitbitOAuth2 = FitbitOAuth2(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            use_callback_server=use_callback_server,
        )

        # Initialize API resources
        self.active_zone: ActiveZoneResource = ActiveZoneResource(
            self.auth.oauth, language=language, locale=locale
        )
        self.activity_timeseries: ActivityTimeSeriesResource = ActivityTimeSeriesResource(
            self.auth.oauth, language=language, locale=locale
        )
        self.activity: ActivityResource = ActivityResource(
            self.auth.oauth, language=language, locale=locale
        )
        self.body_timeseries: BodyTimeSeriesResource = BodyTimeSeriesResource(
            self.auth.oauth, language=language, locale=locale
        )
        self.body: BodyResource = BodyResource(self.auth.oauth, language=language, locale=locale)
        self.breathingrate: BreathingRateResource = BreathingRateResource(
            self.auth.oauth, language=language, locale=locale
        )
        self.cardiofitness: CardioFitnessResource = CardioFitnessResource(
            self.auth.oauth, language=language, locale=locale
        )
        self.device: DeviceResource = DeviceResource(
            self.auth.oauth, language=language, locale=locale
        )
        self.ecg: ECGResource = ECGResource(self.auth.oauth, language=language, locale=locale)
        self.friends: FriendsResource = FriendsResource(
            self.auth.oauth, language=language, locale=locale
        )
        self.heartrate_timeseries: HeartRateTimeSeriesResource = HeartRateTimeSeriesResource(
            self.auth.oauth, language=language, locale=locale
        )
        self.heartrate_variability: HeartRateVariabilityResource = HeartRateVariabilityResource(
            self.auth.oauth, language=language, locale=locale
        )
        self.irregular_rhythm: IrregularRhythmResource = IrregularRhythmResource(
            self.auth.oauth, language=language, locale=locale
        )
        self.nutrition_timeseries: NutritionTimeSeriesResource = NutritionTimeSeriesResource(
            self.auth.oauth, language=language, locale=locale
        )
        self.nutrition: NutritionResource = NutritionResource(
            self.auth.oauth, language=language, locale=locale
        )
        self.sleep: SleepResource = SleepResource(self.auth.oauth, language=language, locale=locale)
        self.spo2: SpO2Resource = SpO2Resource(self.auth.oauth, language=language, locale=locale)
        self.subscription: SubscriptionResource = SubscriptionResource(
            self.auth.oauth, language=language, locale=locale
        )
        self.temperature: TemperatureResource = TemperatureResource(
            self.auth.oauth, language=language, locale=locale
        )
        self.user: UserResource = UserResource(self.auth.oauth, language=language, locale=locale)

    def authenticate(self, force_new: bool = False) -> bool:
        """
        Authenticate with Fitbit API

        Args:
            force_new: Force new authentication even if valid token exists

        Returns:
            bool: True if authenticated successfully
        """
        return self.auth.authenticate(force_new=force_new)
