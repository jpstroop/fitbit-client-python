# Method Naming and Typing

The interns who developed the Fitbit
[Web API](https://dev.fitbit.com/build/reference/web-api/) were not very
consistent with naming of the API endpoints or the responses. Just a few
examples:

- `create_activity_goals` allows you to create one goal at a time

- `add_favorite_foods` adds one food at a time, and "add" is only used here.
  It's "create" everywhere else.

- Method names that suggest they would return a list usually don't. They use the
  structure:

```json
{
  "one-single-key": [
    "and then a list of objects/dicts here...."
  ]
}
```

This would be a lovely and reliable convention! Except that:

- `get_favorite_activities`

- `get_frequent_activities`

- `get_recent_activity_types`

- `get_favorite_activities`

- `get_frequent_activities`

- `get_recent_activity_types`

- `get_devices`

- `get_food_locales`

- `get_food_units`

- `get_frequent_foods`

- `get_recent_foods`

- `get_spo2_summary_by_interval`

All return lists. If there is a rhyme or reason for this, I've not found it yet.

## Naming

Methods are named exactly as they appear in the
[Web API Documentation](https://dev.fitbit.com/build/reference/web-api/). When
there are inconsistencies (frequently) the documentation;s URL slug is the
deciding factor. For example, for "Get AZM Time Series by Date"
https://dev.fitbit.com/build/reference/web-api/active-zone-minutes-timeseries/get-azm-timeseries-by-date/,
(which is it--"Time Series" or "timeseries"?) the method in our code will be
`get_azm_timeseries_by_date()`.

TODO. Explain inconsistencies wrt plurals, aliases, lists vs object, etc.

## Typing

TODO. Explain the convention...

### Method Return Types

#### ActiveZoneMinutesResource

- `get_azm_timeseries_by_date -> Dict[str, JSONType]`
- `get_azm_timeseries_by_interval -> Dict[str, JSONType]`

#### ActivityTimeSeriesResource

- `get_activity_timeseries_by_date -> Dict[str, JSONType]`
- `get_activity_timeseries_by_date_range -> Dict[str, JSONType]`

#### ActivityResource

- `create_activity_goals -> Dict[str, JSONType]`
- `create_activity_goal -> Dict[str, JSONType]` (alias for
  create_activity_goals)
- `create_activity_log -> Dict[str, JSONType]`
- `create_favorite_activity -> Dict[Never, Never]` ??
- `delete_activity_log -> Dict[Never, Never]` ??
- `delete_favorite_activity -> None`
- `get_activity_goals -> Dict[str, JSONType]`
- `get_daily_activity_summary -> Dict[str, JSONType]`
- `get_activity_type -> Dict[str, JSONType]`
- `get_all_activity_types -> Dict[str, JSONType]`
- `get_favorite_activities -> List[JSONType]`
- `get_frequent_activities -> List[JSONType]`
- `get_recent_activity_types -> List[JSONType]`
- `get_lifetime_stats -> Dict[str, JSONType]`
- `get_activity_tcx -> str` (XML)
- `get_activity_log_list -> Dict[str, JSONType]`

#### BaseResource

- `_make_request -> Any`

#### BodyTimeSeriesResource

- `get_body_timeseries_by_date -> Dict[str, JSONType]`
- `get_body_timeseries_by_date_range -> Dict[str, JSONType]`
- `get_bodyfat_timeseries_by_date -> Dict[str, JSONType]`
- `get_bodyfat_timeseries_by_date_range -> Dict[str, JSONType]`
- `get_weight_timeseries_by_date -> Dict[str, JSONType]`
- `get_weight_timeseries_by_date_range -> Dict[str, JSONType]`

#### BodyResource

- `create_bodyfat_goal -> Dict[str, JSONType]`
- `create_bodyfat_log -> Dict[str, JSONType]`
- `create_weight_goal -> Dict[str, JSONType]`
- `create_weight_log -> Dict[str, JSONType]`
- `delete_bodyfat_log -> None`
- `delete_weight_log -> None`
- `get_body_goals -> Dict[str, JSONType]`
- `get_bodyfat_log -> Dict[str, JSONType]`
- `get_weight_logs -> Dict[str, JSONType]`

#### BreathingRateResource

- `get_breathing_rate_summary_by_date -> Dict[str, JSONType]`
- `get_breathing_rate_summary_by_interval -> Dict[str, JSONType]`

#### CardioFitnessScoreResource

- `get_vo2_max_summary_by_date -> Dict[str, JSONType]`
- `get_vo2_max_summary_by_interval -> Dict[str, JSONType]`

#### DeviceResource

- `get_devices -> List[JSONType]`
- `create_alarm` (raises `NotImplementedError`)
- `delete_alarm` (raises `NotImplementedError`)
- `get_alarm` (raises `NotImplementedError`)
- `update_alarm` (raises `NotImplementedError`)

#### ElectrocardiogramResource

- `get_ecg_log_list -> Dict[str, JSONType]`

#### FriendsResource

- `get_friends -> Dict[str, JSONType]`
- `get_friends_leaderboard -> Dict[str, JSONType]`

#### HeartrateTimeSeriesResource

- `get_heartrate_timeseries_by_date -> Dict[str, JSONType]`
- `get_heartrate_timeseries_by_date_range -> Dict[str, JSONType]`

#### HeartrateVariabilityResource

- `get_hrv_summary_by_date -> Dict[str, JSONType]`
- `get_hrv_summary_by_interval -> Dict[str, JSONType]`

#### IntradayResource

- `get_azm_intraday_by_date -> Dict[str, JSONType]`
- `get_azm_intraday_by_interval -> Dict[str, JSONType]`
- `get_activity_intraday_by_date -> Dict[str, JSONType]`
- `get_activity_intraday_by_interval -> Dict[str, JSONType]`
- `get_breathing_rate_intraday_by_date -> Dict[str, JSONType]`
- `get_breathing_rate_intraday_by_interval -> Dict[str, JSONType]`
- `get_heartrate_intraday_by_date -> Dict[str, JSONType]`
- `get_heartrate_intraday_by_interval -> Dict[str, JSONType]`
- `get_hrv_intraday_by_date -> Dict[str, JSONType]`
- `get_hrv_intraday_by_interval -> Dict[str, JSONType]`
- `get_spo2_intraday_by_date -> Dict[str, JSONType]`
- `get_spo2_intraday_by_interval -> Dict[str, JSONType]`

#### IrregularRhythmNotificationsResource

- `get_irn_alerts_list -> Dict[str, JSONType]`
- `get_irn_profile -> Dict[str, JSONType]`

#### NutritionTimeSeriesResource

- `get_nutrition_timeseries_by_date -> Dict[str, JSONType]`
- `get_nutrition_timeseries_by_date_range -> Dict[str, JSONType]`

#### NutritionResource

- `add_favorite_foods -> None`
- `add_favorite_food -> None` (alias for add_favorite_foods)
- `create_favorite_food -> None` (alias for add_favorite_foods)
- `create_food -> Dict[str, JSONType]`
- `create_food_log -> Dict[str, JSONType]`
- `create_food_goal -> Dict[str, JSONType]`
- `create_meal -> Dict[str, JSONType]`
- `create_water_goal -> Dict[str, JSONType]`
- `create_water_log -> Dict[str, JSONType]`
- `delete_custom_food -> None`
- `delete_favorite_foods -> None`
- `delete_favorite_food -> None` (alias for delete_favorite_foods)
- `delete_food_log -> None`
- `delete_meal -> None`
- `delete_water_log -> None`
- `get_food -> Dict[str, JSONType]`
- `get_food_goals -> Dict[str, JSONType]`
- `get_food_log -> Dict[str, JSONType]`
- `get_food_locales -> List[JSONType]`
- `get_food_units -> List[JSONType]`
- `get_frequent_foods -> List[JSONType]`
- `get_recent_foods -> List[JSONType]`
- `get_favorite_foods -> Dict[str, JSONType]`
- `get_meal -> Dict[str, JSONType]`
- `get_meals -> Dict[str, JSONType]`
- `get_water_goal -> Dict[str, JSONType]`
- `get_water_log -> Dict[str, JSONType]`
- `search_foods -> Dict[str, JSONType]`
- `update_food_log -> Dict[str, JSONType]`
- `update_meal -> Dict[str, JSONType]`
- `update_water_log -> Dict[str, JSONType]`

#### SleepResource

- `create_sleep_goals -> Dict[str, JSONType]`
- `create_sleep_goal -> Dict[str, JSONType]` (alias for create_sleep_goals)
- `create_sleep_log -> Dict[str, JSONType]`
- `delete_sleep_log -> None`
- `get_sleep_goals -> Dict[str, JSONType]`
- `get_sleep_goal -> Dict[str, JSONType]` (alias for get_sleep_goals)
- `get_sleep_log_by_date -> Dict[str, JSONType]`
- `get_sleep_log_by_date_range -> Dict[str, JSONType]`
- `get_sleep_log_list -> Dict[str, JSONType]`

#### SpO2Resource

- `get_spo2_summary_by_date -> Dict[str, JSONType]`
- `get_spo2_summary_by_interval -> List[JSONType]`

#### SubscriptionResource

- `get_subscription_list -> Dict[str, JSONType]`
- `create_subscription` (raises `NotImplementedError`)
- `delete_subscription` (raises `NotImplementedError`)

#### TemperatureResource

- `get_temperature_core_summary_by_date -> Dict[str, JSONType]`
- `get_temperature_core_summary_by_interval -> Dict[str, JSONType]`
- `get_temperature_skin_summary_by_date -> Dict[str, JSONType]`
- `get_temperature_skin_summary_by_interval -> Dict[str, JSONType]`

#### UserResource

- `get_profile -> Dict[str, JSONType]`
- `update_profile -> Dict[str, JSONType]`
- `get_badges -> Dict[str, JSONType]`
