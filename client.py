# client.py
from typing import Any
from typing import Dict

from auth import FitbitOAuth2
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


class FitbitClient:
    """Main client for interacting with Fitbit API"""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, **kwargs: Dict[str, Any]) -> None:
        """Initialize the Fitbit client with OAuth2 authentication"""
        self.auth: FitbitOAuth2 = FitbitOAuth2(client_id, client_secret, redirect_uri, **kwargs)

        # Initialize resources
        self.active_zone: ActiveZoneResource = ActiveZoneResource(self.auth.oauth)
        self.activity_timeseries: ActivityTimeSeriesResource = ActivityTimeSeriesResource(self.auth.oauth)
        self.activity: ActivityResource = ActivityResource(self.auth.oauth)
        self.body_timeseries: BodyTimeSeriesResource = BodyTimeSeriesResource(self.auth.oauth)
        self.body: BodyResource = BodyResource(self.auth.oauth)
        self.breathingrate: BreathingRateResource = BreathingRateResource(self.auth.oauth)
        self.cardiofitness: CardioFitnessResource = CardioFitnessResource(self.auth.oauth)
        self.device: DeviceResource = DeviceResource(self.auth.oauth)
        self.ecg: ECGResource = ECGResource(self.auth.oauth)
        self.friends: FriendsResource = FriendsResource(self.auth.oauth)
        self.heartrate_timeseries: HeartRateTimeSeriesResource = HeartRateTimeSeriesResource(self.auth.oauth)
        self.heartrate_variability: HeartRateVariabilityResource = HeartRateVariabilityResource(self.auth.oauth)
        self.irregular_rhythm: IrregularRhythmResource = IrregularRhythmResource(self.auth.oauth)
        self.nutrition_timeseries: NutritionTimeSeriesResource = NutritionTimeSeriesResource(self.auth.oauth)
        self.nutrition: NutritionResource = NutritionResource(self.auth.oauth)
        self.sleep: SleepResource = SleepResource(self.auth.oauth)
        self.spo2: SpO2Resource = SpO2Resource(self.auth.oauth)
        self.subscription: SubscriptionResource = SubscriptionResource(self.auth.oauth)
        self.temperature: TemperatureResource = TemperatureResource(self.auth.oauth)
        self.user: UserResource = UserResource(self.auth.oauth)

    def authenticate(self, force_new: bool = False) -> bool:
        """Authenticate with Fitbit API"""
        return self.auth.authenticate(force_new)
