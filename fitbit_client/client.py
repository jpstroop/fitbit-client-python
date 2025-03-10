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
        max_retries: int = 5,
        retry_after_seconds: int = 30,
        retry_backoff_factor: float = 2.0,
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
            max_retries: Maximum number of retries for rate-limited requests (default: 3)
            retry_after_seconds: Initial wait time in seconds between retries (default: 60)
            retry_backoff_factor: Multiplier for successive retry waits (default: 1.5)
        """
        self.logger = getLogger("fitbit_client")
        self.logger.debug("Initializing Fitbit client")

        self.redirect_uri: str = redirect_uri
        parsed_uri = urlparse(redirect_uri)
        self.logger.debug(
            f"Using redirect URI: {redirect_uri} on {parsed_uri.hostname}:{parsed_uri.port}"
        )

        # Save rate limiting config
        self.max_retries = max_retries
        self.retry_after_seconds = retry_after_seconds
        self.retry_backoff_factor = retry_backoff_factor

        self.logger.debug("Initializing OAuth handler")
        self.auth: FitbitOAuth2 = FitbitOAuth2(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            token_cache_path=token_cache_path,
            use_callback_server=use_callback_server,
        )

        self.logger.debug(
            f"Initializing API resources with language={language}, locale={locale}, "
            f"rate limiting config: max_retries={max_retries}, "
            f"retry_after_seconds={retry_after_seconds}, "
            f"retry_backoff_factor={retry_backoff_factor}"
        )

        # Initialize API resources
        # fmt: off
        # isort: off
        self.active_zone_minutes: ActiveZoneMinutesResource = ActiveZoneMinutesResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.activity_timeseries: ActivityTimeSeriesResource = ActivityTimeSeriesResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.activity: ActivityResource = ActivityResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.body_timeseries: BodyTimeSeriesResource = BodyTimeSeriesResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.body: BodyResource = BodyResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.breathing_rate: BreathingRateResource = BreathingRateResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.cardio_fitness_score: CardioFitnessScoreResource = CardioFitnessScoreResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.device: DeviceResource = DeviceResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.electrocardiogram: ElectrocardiogramResource = ElectrocardiogramResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.friends: FriendsResource = FriendsResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.heartrate_timeseries: HeartrateTimeSeriesResource = HeartrateTimeSeriesResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.heartrate_variability: HeartrateVariabilityResource = HeartrateVariabilityResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.intraday: IntradayResource = IntradayResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.irregular_rhythm_notifications: IrregularRhythmNotificationsResource = IrregularRhythmNotificationsResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.nutrition_timeseries: NutritionTimeSeriesResource = NutritionTimeSeriesResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.nutrition: NutritionResource = NutritionResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.sleep: SleepResource = SleepResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.spo2: SpO2Resource = SpO2Resource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.subscription: SubscriptionResource = SubscriptionResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.temperature: TemperatureResource = TemperatureResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        
        self.user: UserResource = UserResource(
            self.auth.session, locale=locale, language=language,
            max_retries=max_retries, retry_after_seconds=retry_after_seconds, 
            retry_backoff_factor=retry_backoff_factor
        )
        # fmt: on
        # isort: on
        self.logger.debug("Fitbit client initialized successfully")

        # Set up method aliases
        self._set_up_method_aliases()

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

    def _set_up_method_aliases(self) -> None:
        """Set up direct access to resource methods as client attributes for convenience."""
        self.logger.debug("Setting up method aliases")

        # Active Zone Minutes
        self.get_azm_timeseries_by_date = self.active_zone_minutes.get_azm_timeseries_by_date
        self.get_azm_timeseries_by_interval = (
            self.active_zone_minutes.get_azm_timeseries_by_interval
        )

        # Activity Timeseries
        self.get_activity_timeseries_by_date = (
            self.activity_timeseries.get_activity_timeseries_by_date
        )
        self.get_activity_timeseries_by_date_range = (
            self.activity_timeseries.get_activity_timeseries_by_date_range
        )

        # Activity
        self.create_activity_goals = self.activity.create_activity_goals
        self.create_activity_goal = self.activity.create_activity_goal
        self.create_activity_log = self.activity.create_activity_log
        self.get_activity_log_list = self.activity.get_activity_log_list
        self.create_favorite_activity = self.activity.create_favorite_activity
        self.delete_activity_log = self.activity.delete_activity_log
        self.delete_favorite_activity = self.activity.delete_favorite_activity
        self.get_activity_goals = self.activity.get_activity_goals
        self.get_daily_activity_summary = self.activity.get_daily_activity_summary
        self.get_activity_type = self.activity.get_activity_type
        self.get_all_activity_types = self.activity.get_all_activity_types
        self.get_favorite_activities = self.activity.get_favorite_activities
        self.get_frequent_activities = self.activity.get_frequent_activities
        self.get_recent_activity_types = self.activity.get_recent_activity_types
        self.get_lifetime_stats = self.activity.get_lifetime_stats
        self.get_activity_tcx = self.activity.get_activity_tcx

        # Body Timeseries
        self.get_body_timeseries_by_date = self.body_timeseries.get_body_timeseries_by_date
        self.get_body_timeseries_by_date_range = (
            self.body_timeseries.get_body_timeseries_by_date_range
        )
        self.get_bodyfat_timeseries_by_date = self.body_timeseries.get_bodyfat_timeseries_by_date
        self.get_bodyfat_timeseries_by_date_range = (
            self.body_timeseries.get_bodyfat_timeseries_by_date_range
        )
        self.get_weight_timeseries_by_date = self.body_timeseries.get_weight_timeseries_by_date
        self.get_weight_timeseries_by_date_range = (
            self.body_timeseries.get_weight_timeseries_by_date_range
        )

        # Body
        self.create_bodyfat_goal = self.body.create_bodyfat_goal
        self.create_bodyfat_log = self.body.create_bodyfat_log
        self.create_weight_goal = self.body.create_weight_goal
        self.create_weight_log = self.body.create_weight_log
        self.delete_bodyfat_log = self.body.delete_bodyfat_log
        self.delete_weight_log = self.body.delete_weight_log
        self.get_body_goals = self.body.get_body_goals
        self.get_bodyfat_log = self.body.get_bodyfat_log
        self.get_weight_logs = self.body.get_weight_logs

        # Breathing Rate
        self.get_breathing_rate_summary_by_date = (
            self.breathing_rate.get_breathing_rate_summary_by_date
        )
        self.get_breathing_rate_summary_by_interval = (
            self.breathing_rate.get_breathing_rate_summary_by_interval
        )

        # Cardio Fitness Score
        self.get_vo2_max_summary_by_date = self.cardio_fitness_score.get_vo2_max_summary_by_date
        self.get_vo2_max_summary_by_interval = (
            self.cardio_fitness_score.get_vo2_max_summary_by_interval
        )

        # Device
        self.get_devices = self.device.get_devices

        # Electrocardiogram
        self.get_ecg_log_list = self.electrocardiogram.get_ecg_log_list

        # Friends
        self.get_friends = self.friends.get_friends
        self.get_friends_leaderboard = self.friends.get_friends_leaderboard

        # Heartrate Timeseries
        self.get_heartrate_timeseries_by_date = (
            self.heartrate_timeseries.get_heartrate_timeseries_by_date
        )
        self.get_heartrate_timeseries_by_date_range = (
            self.heartrate_timeseries.get_heartrate_timeseries_by_date_range
        )

        # Heartrate Variability
        self.get_hrv_summary_by_date = self.heartrate_variability.get_hrv_summary_by_date
        self.get_hrv_summary_by_interval = self.heartrate_variability.get_hrv_summary_by_interval

        # Intraday
        self.get_azm_intraday_by_date = self.intraday.get_azm_intraday_by_date
        self.get_azm_intraday_by_interval = self.intraday.get_azm_intraday_by_interval
        self.get_activity_intraday_by_date = self.intraday.get_activity_intraday_by_date
        self.get_activity_intraday_by_interval = self.intraday.get_activity_intraday_by_interval
        self.get_breathing_rate_intraday_by_date = self.intraday.get_breathing_rate_intraday_by_date
        self.get_breathing_rate_intraday_by_interval = (
            self.intraday.get_breathing_rate_intraday_by_interval
        )
        self.get_heartrate_intraday_by_date = self.intraday.get_heartrate_intraday_by_date
        self.get_heartrate_intraday_by_interval = self.intraday.get_heartrate_intraday_by_interval
        self.get_hrv_intraday_by_date = self.intraday.get_hrv_intraday_by_date
        self.get_hrv_intraday_by_interval = self.intraday.get_hrv_intraday_by_interval
        self.get_spo2_intraday_by_date = self.intraday.get_spo2_intraday_by_date
        self.get_spo2_intraday_by_interval = self.intraday.get_spo2_intraday_by_interval

        # Irregular Rhythm Notifications
        self.get_irn_alerts_list = self.irregular_rhythm_notifications.get_irn_alerts_list
        self.get_irn_profile = self.irregular_rhythm_notifications.get_irn_profile

        # Nutrition Timeseries
        self.get_nutrition_timeseries_by_date = (
            self.nutrition_timeseries.get_nutrition_timeseries_by_date
        )
        self.get_nutrition_timeseries_by_date_range = (
            self.nutrition_timeseries.get_nutrition_timeseries_by_date_range
        )

        # Nutrition
        self.add_favorite_foods = self.nutrition.add_favorite_foods
        self.add_favorite_food = self.nutrition.add_favorite_food
        self.create_favorite_food = self.nutrition.create_favorite_food
        self.create_food = self.nutrition.create_food
        self.create_food_log = self.nutrition.create_food_log
        self.create_food_goal = self.nutrition.create_food_goal
        self.create_meal = self.nutrition.create_meal
        self.create_water_goal = self.nutrition.create_water_goal
        self.create_water_log = self.nutrition.create_water_log
        self.delete_custom_food = self.nutrition.delete_custom_food
        self.delete_favorite_foods = self.nutrition.delete_favorite_foods
        self.delete_favorite_food = self.nutrition.delete_favorite_food
        self.delete_food_log = self.nutrition.delete_food_log
        self.delete_meal = self.nutrition.delete_meal
        self.delete_water_log = self.nutrition.delete_water_log
        self.get_food = self.nutrition.get_food
        self.get_food_goals = self.nutrition.get_food_goals
        self.get_food_log = self.nutrition.get_food_log
        self.get_food_locales = self.nutrition.get_food_locales
        self.get_food_units = self.nutrition.get_food_units
        self.get_frequent_foods = self.nutrition.get_frequent_foods
        self.get_recent_foods = self.nutrition.get_recent_foods
        self.get_favorite_foods = self.nutrition.get_favorite_foods
        self.get_meal = self.nutrition.get_meal
        self.get_meals = self.nutrition.get_meals
        self.get_water_goal = self.nutrition.get_water_goal
        self.get_water_log = self.nutrition.get_water_log
        self.search_foods = self.nutrition.search_foods
        self.update_food_log = self.nutrition.update_food_log
        self.update_meal = self.nutrition.update_meal
        self.update_water_log = self.nutrition.update_water_log

        # Sleep
        self.create_sleep_goals = self.sleep.create_sleep_goals
        self.create_sleep_goal = self.sleep.create_sleep_goal
        self.create_sleep_log = self.sleep.create_sleep_log
        self.delete_sleep_log = self.sleep.delete_sleep_log
        self.get_sleep_goals = self.sleep.get_sleep_goals
        self.get_sleep_goal = self.sleep.get_sleep_goal
        self.get_sleep_log_by_date = self.sleep.get_sleep_log_by_date
        self.get_sleep_log_by_date_range = self.sleep.get_sleep_log_by_date_range
        self.get_sleep_log_list = self.sleep.get_sleep_log_list

        # SpO2
        self.get_spo2_summary_by_date = self.spo2.get_spo2_summary_by_date
        self.get_spo2_summary_by_interval = self.spo2.get_spo2_summary_by_interval

        # Subscription
        self.get_subscription_list = self.subscription.get_subscription_list

        # Temperature
        self.get_temperature_core_summary_by_date = (
            self.temperature.get_temperature_core_summary_by_date
        )
        self.get_temperature_core_summary_by_interval = (
            self.temperature.get_temperature_core_summary_by_interval
        )
        self.get_temperature_skin_summary_by_date = (
            self.temperature.get_temperature_skin_summary_by_date
        )
        self.get_temperature_skin_summary_by_interval = (
            self.temperature.get_temperature_skin_summary_by_interval
        )

        # User
        self.get_profile = self.user.get_profile
        self.update_profile = self.user.update_profile
        self.get_badges = self.user.get_badges

        self.logger.debug("Method aliases set up successfully")
