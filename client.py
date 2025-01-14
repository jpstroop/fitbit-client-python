# from resources.activity import ActivityResource
# from resources.device import DeviceResource
# from resources.heart import HeartResource
# from resources.sleep import SleepResource
from auth import FitbitOAuth2
from resources.nutrition import NutritionResource
from resources.profile import ProfileResource
from typing import Any
from typing import Dict


class FitbitClient:
    """Main client for interacting with Fitbit API"""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, **kwargs: Dict[str, Any]) -> None:
        self.auth: FitbitOAuth2 = FitbitOAuth2(client_id, client_secret, redirect_uri, **kwargs)

        # Initialize resources
        self.profile: ProfileResource = ProfileResource(self.auth.oauth)
        self.nutrition: NutritionResource = NutritionResource(self.auth.oauth)
        # self.activity: ActivityResource = ActivityResource(self.auth.oauth)
        # self.heart: HeartResource = HeartResource(self.auth.oauth)
        # self.sleep: SleepResource = SleepResource(self.auth.oauth)
        # self.device: DeviceResource = DeviceResource(self.auth.oauth)

    def authenticate(self, force_new: bool = False) -> bool:
        """Authenticate with Fitbit API"""
        return self.auth.authenticate(force_new)
