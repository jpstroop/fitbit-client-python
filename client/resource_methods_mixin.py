# client/resource_methods_mixin.py
# Standard library imports
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

# Local imports
from resources.constants import ActivityGoalType
from resources.constants import BodyGoalType
from resources.constants import BodyResourceType
from resources.constants import BodyTimePeriod
from resources.constants import ClockTimeFormat
from resources.constants import FoodFormType
from resources.constants import FoodPlanIntensity
from resources.constants import Gender
from resources.constants import MealType
from resources.constants import NutritionResource as NutritionResourceType
from resources.constants import Period
from resources.constants import SleepType
from resources.constants import StartDayOfWeek
from resources.constants import SubscriptionCategory
from resources.constants import WaterUnit
from resources.constants import WeekDay


class ClientMethodsMixin():
    """
    Mixin class that provides direct access to resource methods on the client.
    Method names are only changed when there are naming collisions across resources.
    """
    # Active Zone Minutes Methods
    def get_azm_by_date(self, date: str, period: Period, user_id: str = "-") -> Dict[str, Any]:
        """Gets Active Zone Minutes data for a specific date. See ActiveZoneResource.get_azm_by_date() for full documentation."""
        return self.active_zone.get_azm_by_date(date, period, user_id)

    def get_azm_by_date_range(
        self, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Gets Active Zone Minutes data for a date range. See ActiveZoneResource.get_azm_by_date_range() for full documentation."""
        return self.active_zone.get_azm_by_date_range(start_date, end_date, user_id)

    # Activity Methods
    def create_activity_goal(
        self, period: str, type: ActivityGoalType, value: int, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Creates or updates an activity goal. See ActivityResource.create_activity_goal() for full documentation."""
        return self.activity.create_activity_goal(period, type, value, user_id)

    def create_activity_log(self, **kwargs) -> Dict[str, Any]:
        """Creates an activity log entry. See ActivityResource.create_activity_log() for full documentation."""
        return self.activity.create_activity_log(**kwargs)

    def get_activity_logs(self, **kwargs) -> Dict[str, Any]:
        """Gets activity log entries. See ActivityResource.get_activity_logs() for full documentation."""
        return self.activity.get_activity_logs(**kwargs)

    def create_favorite_activity(self, activity_id: str, user_id: str = "-") -> Dict[str, Any]:
        """Adds an activity to favorites. See ActivityResource.create_favorite_activity() for full documentation."""
        return self.activity.create_favorite_activity(activity_id, user_id)

    def delete_activity_log(self, activity_log_id: str, user_id: str = "-") -> Dict[str, Any]:
        """Deletes an activity log entry. See ActivityResource.delete_activity_log() for full documentation."""
        return self.activity.delete_activity_log(activity_log_id, user_id)

    def delete_favorite_activity(self, activity_id: str, user_id: str = "-") -> Dict[str, Any]:
        """Removes an activity from favorites. See ActivityResource.delete_favorite_activity() for full documentation."""
        return self.activity.delete_favorite_activity(activity_id, user_id)

    def get_activity_goals(self, period: str, user_id: str = "-") -> Dict[str, Any]:
        """Gets activity goals. See ActivityResource.get_activity_goals() for full documentation."""
        return self.activity.get_activity_goals(period, user_id)

    def get_daily_activity_summary(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """Gets daily activity summary. See ActivityResource.get_daily_activity_summary() for full documentation."""
        return self.activity.get_daily_activity_summary(date, user_id)

    def get_activity_type(self, activity_id: str) -> Dict[str, Any]:
        """Gets activity type details. See ActivityResource.get_activity_type() for full documentation."""
        return self.activity.get_activity_type(activity_id)

    def get_all_activity_types(self) -> Dict[str, Any]:
        """Gets all activity types. See ActivityResource.get_all_activity_types() for full documentation."""
        return self.activity.get_all_activity_types()

    def get_favorite_activities(self, user_id: str = "-") -> Dict[str, Any]:
        """Gets favorite activities. See ActivityResource.get_favorite_activities() for full documentation."""
        return self.activity.get_favorite_activities(user_id)

    def get_frequent_activities(self, user_id: str = "-") -> Dict[str, Any]:
        """Gets frequently logged activities. See ActivityResource.get_frequent_activities() for full documentation."""
        return self.activity.get_frequent_activities(user_id)

    def get_recent_activities(self, user_id: str = "-") -> Dict[str, Any]:
        """Gets recently logged activities. See ActivityResource.get_recent_activities() for full documentation."""
        return self.activity.get_recent_activities(user_id)

    def get_lifetime_stats(self, user_id: str = "-") -> Dict[str, Any]:
        """Gets lifetime activity statistics. See ActivityResource.get_lifetime_stats() for full documentation."""
        return self.activity.get_lifetime_stats(user_id)

    def get_activity_tcx(
        self, log_id: str, include_partial_tcx: bool = False, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Gets TCX data for an activity. See ActivityResource.get_activity_tcx() for full documentation."""
        return self.activity.get_activity_tcx(log_id, include_partial_tcx, user_id)

    # Activity Time Series Methods (renamed due to collision)
    def get_activity_time_series(
        self, resource_path: str, date: str, period: Period, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Gets activity time series data. Renamed from get_time_series() to avoid naming conflicts. See ActivityTimeSeriesResource.get_time_series() for full documentation."""
        return self.activity_timeseries.get_time_series(resource_path, date, period, user_id)

    def get_activity_time_series_by_date_range(
        self, resource_path: str, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Gets activity time series data by date range. Renamed from get_time_series_by_date_range() to avoid naming conflicts. See ActivityTimeSeriesResource.get_time_series_by_date_range() for full documentation."""
        return self.activity_timeseries.get_time_series_by_date_range(
            resource_path, start_date, end_date, user_id
        )

    # Body Methods
    def create_body_fat_goal(self, fat: float, user_id: str = "-") -> Dict[str, Any]:
        """Creates a body fat goal. See BodyResource.create_body_fat_goal() for full documentation."""
        return self.body.create_body_fat_goal(fat, user_id)

    def create_body_fat_log(
        self, fat: float, date: str, time: Optional[str] = None, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Creates a body fat log entry. See BodyResource.create_body_fat_log() for full documentation."""
        return self.body.create_body_fat_log(fat, date, time, user_id)

    def create_weight_goal(
        self,
        start_date: str,
        start_weight: float,
        weight: Optional[float] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """Creates a weight goal. See BodyResource.create_weight_goal() for full documentation."""
        return self.body.create_weight_goal(start_date, start_weight, weight, user_id)

    def create_weight_log(
        self, weight: float, date: str, time: Optional[str] = None, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Creates a weight log entry. See BodyResource.create_weight_log() for full documentation."""
        return self.body.create_weight_log(weight, date, time, user_id)

    def delete_body_fat_log(self, body_fat_log_id: str, user_id: str = "-") -> Dict[str, Any]:
        """Deletes a body fat log entry. See BodyResource.delete_body_fat_log() for full documentation."""
        return self.body.delete_body_fat_log(body_fat_log_id, user_id)

    def delete_weight_log(self, weight_log_id: str, user_id: str = "-") -> Dict[str, Any]:
        """Deletes a weight log entry. See BodyResource.delete_weight_log() for full documentation."""
        return self.body.delete_weight_log(weight_log_id, user_id)

    def get_body_goals(self, goal_type: BodyGoalType, user_id: str = "-") -> Dict[str, Any]:
        """Gets body measurement goals. See BodyResource.get_body_goals() for full documentation."""
        return self.body.get_body_goals(goal_type, user_id)

    def get_body_fat_logs(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """Gets body fat log entries. See BodyResource.get_body_fat_logs() for full documentation."""
        return self.body.get_body_fat_logs(date, user_id)

    def get_weight_logs(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """Gets weight log entries. See BodyResource.get_weight_logs() for full documentation."""
        return self.body.get_weight_logs(date, user_id)

    # Body Time Series Methods (renamed due to collision)
    def get_body_time_series_by_date(
        self, resource_type: BodyResourceType, date: str, period: BodyTimePeriod, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Gets body time series data. Renamed from get_time_series_by_date() to avoid naming conflicts. See BodyTimeSeriesResource.get_time_series_by_date() for full documentation."""
        return self.body_timeseries.get_time_series_by_date(resource_type, date, period, user_id)

    # Breathing Rate Methods
    def get_breathing_rate_summary_by_date(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """Gets breathing rate data for a date. See BreathingRateResource.get_breathing_rate_summary_by_date() for full documentation."""
        return self.breathingrate.get_breathing_rate_summary_by_date(date, user_id)

    def get_breathing_rate_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Gets breathing rate data for a date range. See BreathingRateResource.get_breathing_rate_summary_by_interval() for full documentation."""
        return self.breathingrate.get_breathing_rate_summary_by_interval(
            start_date, end_date, user_id
        )

    # Cardio Fitness Methods
    def get_vo2_max_summary_by_date(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """Gets VO2 Max data for a date. See CardioFitnessResource.get_vo2_max_summary_by_date() for full documentation."""
        return self.cardiofitness.get_vo2_max_summary_by_date(date, user_id)

    def get_vo2_max_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Gets VO2 Max data for a date range. See CardioFitnessResource.get_vo2_max_summary_by_interval() for full documentation."""
        return self.cardiofitness.get_vo2_max_summary_by_interval(start_date, end_date, user_id)

    # Device Methods
    def create_alarm(
        self,
        tracker_id: str,
        time: str,
        enabled: bool,
        recurring: bool,
        week_days: List[WeekDay],
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """Creates a device alarm. See DeviceResource.create_alarm() for full documentation."""
        return self.device.create_alarm(tracker_id, time, enabled, recurring, week_days, user_id)

    def delete_alarm(self, tracker_id: str, alarm_id: str, user_id: str = "-") -> Dict[str, Any]:
        """Deletes a device alarm. See DeviceResource.delete_alarm() for full documentation."""
        return self.device.delete_alarm(tracker_id, alarm_id, user_id)

    def get_alarms(self, tracker_id: str, user_id: str = "-") -> Dict[str, Any]:
        """Gets device alarms. See DeviceResource.get_alarms() for full documentation."""
        return self.device.get_alarms(tracker_id, user_id)

    def get_devices(self, user_id: str = "-") -> Dict[str, Any]:
        """Gets list of devices. See DeviceResource.get_devices() for full documentation."""
        return self.device.get_devices(user_id)

    def update_alarm(
        self,
        tracker_id: str,
        alarm_id: str,
        time: str,
        enabled: bool,
        recurring: bool,
        week_days: List[WeekDay],
        snooze_length: int,
        snooze_count: int,
        label: str = None,
        vibe: str = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """Updates a device alarm. See DeviceResource.update_alarm() for full documentation."""
        return self.device.update_alarm(
            tracker_id,
            alarm_id,
            time,
            enabled,
            recurring,
            week_days,
            snooze_length,
            snooze_count,
            label,
            vibe,
            user_id,
        )

    # ECG Methods
    def get_ecg_log_list(
        self,
        before_date: Optional[str] = None,
        after_date: Optional[str] = None,
        sort: str = "desc",
        limit: int = 10,
        offset: int = 0,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """Gets ECG log entries. See ECGResource.get_ecg_log_list() for full documentation."""
        return self.ecg.get_ecg_log_list(before_date, after_date, sort, limit, offset, user_id)

    # Friends Methods
    def get_friends(self, user_id: str = "-") -> Dict[str, Any]:
        """Gets user's friends list. See FriendsResource.get_friends() for full documentation."""
        return self.friends.get_friends(user_id)

    def get_friends_leaderboard(self, user_id: str = "-") -> Dict[str, Any]:
        """Gets friends leaderboard. See FriendsResource.get_friends_leaderboard() for full documentation."""
        return self.friends.get_friends_leaderboard(user_id)

    # Heart Rate Methods (continued from previous implementation)
    def get_heartrate_by_date(
        self, date: str, period: Period, user_id: str = "-", timezone: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gets heart rate data for a date. See HeartRateTimeSeriesResource.get_time_series_by_date() for full documentation."""
        return self.heartrate_timeseries.get_time_series_by_date(date, period, user_id, timezone)

    def get_heartrate_by_date_range(
        self, start_date: str, end_date: str, user_id: str = "-", timezone: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gets heart rate data for a date range. See HeartRateTimeSeriesResource.get_time_series_by_date_range() for full documentation."""
        return self.heartrate_timeseries.get_time_series_by_date_range(
            start_date, end_date, user_id, timezone
        )

    # Heart Rate Variability Methods
    def get_hrv_summary_by_date(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """Gets HRV summary for a date. See HeartRateVariabilityResource.get_hrv_summary_by_date() for full documentation."""
        return self.heartrate_variability.get_hrv_summary_by_date(date, user_id)

    def get_hrv_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Gets HRV summary for a date range. See HeartRateVariabilityResource.get_hrv_summary_by_interval() for full documentation."""
        return self.heartrate_variability.get_hrv_summary_by_interval(start_date, end_date, user_id)

    # Irregular Rhythm Methods
    def get_irregular_rhythm_alerts_list(
        self,
        sort: str,
        limit: int = 10,
        offset: int = 0,
        before_date: Optional[str] = None,
        after_date: Optional[str] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """Gets irregular rhythm alerts. See IrregularRhythmResource.get_alerts_list() for full documentation."""
        return self.irregular_rhythm.get_alerts_list(
            sort, limit, offset, before_date, after_date, user_id
        )

    def get_irregular_rhythm_profile(self, user_id: str = "-") -> Dict[str, Any]:
        """Gets irregular rhythm profile. See IrregularRhythmResource.get_profile() for full documentation."""
        return self.irregular_rhythm.get_profile(user_id)

    # Nutrition Methods
    def add_favorite_food(self, food_id: int, user_id: str = "-") -> Dict[str, Any]:
        """Adds a food to favorites. See NutritionResource.add_favorite_food() for full documentation."""
        return self.nutrition.add_favorite_food(food_id, user_id)

    def create_food(
        self,
        name: str,
        default_food_measurement_unit_id: int,
        default_serving_size: float,
        calories: int,
        description: str,
        form_type: FoodFormType,
        nutritional_values: Dict[str, float],
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """Creates a new food entry. See NutritionResource.create_food() for full documentation."""
        return self.nutrition.create_food(
            name,
            default_food_measurement_unit_id,
            default_serving_size,
            calories,
            description,
            form_type,
            nutritional_values,
            user_id,
        )

    def create_food_log(
        self,
        date: str,
        meal_type_id: MealType,
        unit_id: int,
        amount: float,
        food_id: Optional[int] = None,
        food_name: Optional[str] = None,
        favorite: bool = False,
        brand_name: Optional[str] = None,
        calories: Optional[int] = None,
        nutritional_values: Optional[Dict[str, float]] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """Creates a food log entry. See NutritionResource.create_food_log() for full documentation."""
        return self.nutrition.create_food_log(
            date,
            meal_type_id,
            unit_id,
            amount,
            food_id,
            food_name,
            favorite,
            brand_name,
            calories,
            nutritional_values,
            user_id,
        )

    def create_food_goal(
        self,
        calories: Optional[int] = None,
        intensity: Optional[FoodPlanIntensity] = None,
        personalized: Optional[bool] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """Creates or updates food goals. See NutritionResource.create_food_goal() for full documentation."""
        return self.nutrition.create_food_goal(calories, intensity, personalized, user_id)

    def create_meal(
        self, name: str, description: str, foods: List[Dict[str, Any]], user_id: str = "-"
    ) -> Dict[str, Any]:
        """Creates a meal. See NutritionResource.create_meal() for full documentation."""
        return self.nutrition.create_meal(name, description, foods, user_id)

    def create_water_goal(self, target: float, user_id: str = "-") -> Dict[str, Any]:
        """Creates or updates water goal. See NutritionResource.create_water_goal() for full documentation."""
        return self.nutrition.create_water_goal(target, user_id)

    def create_water_log(
        self, amount: float, date: str, unit: Optional[WaterUnit] = None, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Creates a water log entry. See NutritionResource.create_water_log() for full documentation."""
        return self.nutrition.create_water_log(amount, date, unit, user_id)

    def delete_custom_food(self, food_id: int, user_id: str = "-") -> Dict[str, Any]:
        """Deletes a custom food. See NutritionResource.delete_custom_food() for full documentation."""
        return self.nutrition.delete_custom_food(food_id, user_id)

    def delete_favorite_food(self, food_id: int, user_id: str = "-") -> Dict[str, Any]:
        """Removes a food from favorites. See NutritionResource.delete_favorite_food() for full documentation."""
        return self.nutrition.delete_favorite_food(food_id, user_id)

    def delete_food_log(self, food_log_id: int, user_id: str = "-") -> Dict[str, Any]:
        """Deletes a food log entry. See NutritionResource.delete_food_log() for full documentation."""
        return self.nutrition.delete_food_log(food_log_id, user_id)

    def delete_meal(self, meal_id: int, user_id: str = "-") -> Dict[str, Any]:
        """Deletes a meal. See NutritionResource.delete_meal() for full documentation."""
        return self.nutrition.delete_meal(meal_id, user_id)

    def delete_water_log(self, water_log_id: int, user_id: str = "-") -> Dict[str, Any]:
        """Deletes a water log entry. See NutritionResource.delete_water_log() for full documentation."""
        return self.nutrition.delete_water_log(water_log_id, user_id)

    def get_food(self, food_id: int) -> Dict[str, Any]:
        """Gets food details. See NutritionResource.get_food() for full documentation."""
        return self.nutrition.get_food(food_id)

    def get_food_goals(self, user_id: str = "-") -> Dict[str, Any]:
        """Gets food goals. See NutritionResource.get_food_goals() for full documentation."""
        return self.nutrition.get_food_goals(user_id)

    def get_food_log(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """Gets food log entries. See NutritionResource.get_food_log() for full documentation."""
        return self.nutrition.get_food_log(date, user_id)

    def get_food_locales(self) -> Dict[str, Any]:
        """Gets food locales. See NutritionResource.get_food_locales() for full documentation."""
        return self.nutrition.get_food_locales()

    def get_food_units(self) -> Dict[str, Any]:
        """Gets food units. See NutritionResource.get_food_units() for full documentation."""
        return self.nutrition.get_food_units()

    def get_frequent_foods(self, user_id: str = "-") -> Dict[str, Any]:
        """Gets frequently logged foods. See NutritionResource.get_frequent_foods() for full documentation."""
        return self.nutrition.get_frequent_foods(user_id)

    def get_favorite_foods(self, user_id: str = "-") -> Dict[str, Any]:
        """Gets favorite foods. See NutritionResource.get_favorite_foods() for full documentation."""
        return self.nutrition.get_favorite_foods(user_id)

    def get_meal(self, meal_id: int, user_id: str = "-") -> Dict[str, Any]:
        """Gets meal details. See NutritionResource.get_meal() for full documentation."""
        return self.nutrition.get_meal(meal_id, user_id)

    def get_meals(self, user_id: str = "-") -> Dict[str, Any]:
        """Gets all meals. See NutritionResource.get_meals() for full documentation."""
        return self.nutrition.get_meals(user_id)

    def get_recent_foods(self, user_id: str = "-") -> Dict[str, Any]:
        """Gets recently logged foods. See NutritionResource.get_recent_foods() for full documentation."""
        return self.nutrition.get_recent_foods(user_id)

    def get_water_goal(self, user_id: str = "-") -> Dict[str, Any]:
        """Gets water goal. See NutritionResource.get_water_goal() for full documentation."""
        return self.nutrition.get_water_goal(user_id)

    def get_water_log(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """Gets water log entries. See NutritionResource.get_water_log() for full documentation."""
        return self.nutrition.get_water_log(date, user_id)

    def search_foods(self, query: str) -> Dict[str, Any]:
        """Searches for foods. See NutritionResource.search_foods() for full documentation."""
        return self.nutrition.search_foods(query)

    def update_food_log(
        self,
        food_log_id: int,
        meal_type_id: MealType,
        unit_id: Optional[int] = None,
        amount: Optional[float] = None,
        calories: Optional[int] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """Updates a food log entry. See NutritionResource.update_food_log() for full documentation."""
        return self.nutrition.update_food_log(
            food_log_id, meal_type_id, unit_id, amount, calories, user_id
        )

    def update_meal(
        self,
        meal_id: int,
        name: str,
        description: str,
        foods: List[Dict[str, Any]],
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """Updates a meal. See NutritionResource.update_meal() for full documentation."""
        return self.nutrition.update_meal(meal_id, name, description, foods, user_id)

    def update_water_log(
        self, water_log_id: int, amount: float, unit: Optional[WaterUnit] = None, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Updates a water log entry. See NutritionResource.update_water_log() for full documentation."""
        return self.nutrition.update_water_log(water_log_id, amount, unit, user_id)

    # Nutrition Time Series Methods
    def get_nutrition_time_series_by_date(
        self, resource: NutritionResourceType, date: str, period: Period, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Gets nutrition time series data for a period starting from a date. See NutritionTimeSeriesResource.get_time_series_by_date() for full documentation."""
        return self.nutrition_timeseries.get_time_series_by_date(resource, date, period, user_id)

    def get_nutrition_time_series_by_date_range(
        self, resource: NutritionResourceType, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Gets nutrition time series data for a date range. See NutritionTimeSeriesResource.get_time_series_by_date_range() for full documentation."""
        return self.nutrition_timeseries.get_time_series_by_date_range(
            resource, start_date, end_date, user_id
        )

    # Sleep Methods
    def create_sleep_goal(self, min_duration: int, user_id: str = "-") -> Dict[str, Any]:
        """Creates or updates sleep goal. See SleepResource.create_sleep_goal() for full documentation."""
        return self.sleep.create_sleep_goal(min_duration, user_id)

    def log_sleep(
        self,
        start_time: str,
        duration_millis: int,
        date: str,
        sleep_type: SleepType = SleepType.CLASSIC,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """Logs a sleep event. See SleepResource.log_sleep() for full documentation."""
        return self.sleep.log_sleep(start_time, duration_millis, date, sleep_type, user_id)

    def delete_sleep_log(self, log_id: str, user_id: str = "-") -> Dict[str, Any]:
        """Deletes a sleep log entry. See SleepResource.delete_sleep_log() for full documentation."""
        return self.sleep.delete_sleep_log(log_id, user_id)

    def get_sleep_goal(self, user_id: str = "-") -> Dict[str, Any]:
        """Gets sleep goal. See SleepResource.get_sleep_goal() for full documentation."""
        return self.sleep.get_sleep_goal(user_id)

    def get_sleep_logs(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """Gets sleep logs for a date. See SleepResource.get_sleep_logs() for full documentation."""
        return self.sleep.get_sleep_logs(date, user_id)

    def get_sleep_logs_by_date_range(
        self, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Gets sleep logs for a date range. See SleepResource.get_sleep_logs_by_date_range() for full documentation."""
        return self.sleep.get_sleep_logs_by_date_range(start_date, end_date, user_id)

    def get_sleep_logs_list(
        self,
        before_date: Optional[str] = None,
        after_date: Optional[str] = None,
        sort: str = "desc",
        limit: int = 100,
        offset: int = 0,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """Gets list of sleep logs. See SleepResource.get_sleep_logs_list() for full documentation."""
        return self.sleep.get_sleep_logs_list(before_date, after_date, sort, limit, offset, user_id)

    # SpO2 Methods
    def get_spo2_summary_by_date(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """Gets SpO2 data for a date. See SpO2Resource.get_summary_by_date() for full documentation."""
        return self.spo2.get_summary_by_date(date, user_id)

    def get_spo2_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Gets SpO2 data for a date range. See SpO2Resource.get_summary_by_interval() for full documentation."""
        return self.spo2.get_summary_by_interval(start_date, end_date, user_id)

    # Subscription Methods
    def create_subscription(
        self,
        subscription_id: str,
        category: Optional[SubscriptionCategory] = None,
        subscriber_id: Optional[str] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """Creates a subscription for notifications. See SubscriptionResource.create_subscription() for full documentation."""
        return self.subscription.create_subscription(
            subscription_id, category, subscriber_id, user_id
        )

    def delete_subscription(
        self,
        subscription_id: str,
        category: Optional[SubscriptionCategory] = None,
        subscriber_id: Optional[str] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """Deletes a subscription. See SubscriptionResource.delete_subscription() for full documentation."""
        return self.subscription.delete_subscription(
            subscription_id, category, subscriber_id, user_id
        )

    def get_subscription_list(
        self,
        category: Optional[SubscriptionCategory] = None,
        subscriber_id: Optional[str] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """Gets list of subscriptions. See SubscriptionResource.get_subscription_list() for full documentation."""
        return self.subscription.get_subscription_list(category, subscriber_id, user_id)

    # Temperature Methods
    def get_core_temperature_summary_by_date(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """Gets core temperature data for a date. See TemperatureResource.get_core_summary_by_date() for full documentation."""
        return self.temperature.get_core_summary_by_date(date, user_id)

    def get_core_temperature_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Gets core temperature data for a date range. See TemperatureResource.get_core_summary_by_interval() for full documentation."""
        return self.temperature.get_core_summary_by_interval(start_date, end_date, user_id)

    def get_skin_temperature_summary_by_date(self, date: str, user_id: str = "-") -> Dict[str, Any]:
        """Gets skin temperature data for a date. See TemperatureResource.get_skin_summary_by_date() for full documentation."""
        return self.temperature.get_skin_summary_by_date(date, user_id)

    def get_skin_temperature_summary_by_interval(
        self, start_date: str, end_date: str, user_id: str = "-"
    ) -> Dict[str, Any]:
        """Gets skin temperature data for a date range. See TemperatureResource.get_skin_summary_by_interval() for full documentation."""
        return self.temperature.get_skin_summary_by_interval(start_date, end_date, user_id)

    # User Methods
    def get_profile(self, user_id: str = "-") -> Dict[str, Any]:
        """Gets user profile information. See UserResource.get_profile() for full documentation."""
        return self.user.get_profile(user_id)

    def update_profile(
        self,
        gender: Optional[Gender] = None,
        birthday: Optional[str] = None,
        height: Optional[str] = None,
        about_me: Optional[str] = None,
        full_name: Optional[str] = None,
        country: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        clock_time_display_format: Optional[ClockTimeFormat] = None,
        start_day_of_week: Optional[StartDayOfWeek] = None,
        locale: Optional[str] = None,
        locale_lang: Optional[str] = None,
        locale_country: Optional[str] = None,
        timezone: Optional[str] = None,
        foods_locale: Optional[str] = None,
        glucose_unit: Optional[str] = None,
        height_unit: Optional[str] = None,
        water_unit: Optional[str] = None,
        weight_unit: Optional[str] = None,
        stride_length_walking: Optional[str] = None,
        stride_length_running: Optional[str] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """Updates user profile information. See UserResource.update_profile() for full documentation."""
        return self.user.update_profile(
            gender=gender,
            birthday=birthday,
            height=height,
            about_me=about_me,
            full_name=full_name,
            country=country,
            state=state,
            city=city,
            clock_time_display_format=clock_time_display_format,
            start_day_of_week=start_day_of_week,
            locale=locale,
            locale_lang=locale_lang,
            locale_country=locale_country,
            timezone=timezone,
            foods_locale=foods_locale,
            glucose_unit=glucose_unit,
            height_unit=height_unit,
            water_unit=water_unit,
            weight_unit=weight_unit,
            stride_length_walking=stride_length_walking,
            stride_length_running=stride_length_running,
            user_id=user_id,
        )

    def get_badges(self, user_id: str = "-") -> Dict[str, Any]:
        """Gets user's achievement badges. See UserResource.get_badges() for full documentation."""
        return self.user.get_badges(user_id)
