# Method Naming and Typing

Typing and JSON is awkward, but it's useful to know what you should expect to
get back when you call a method. For this reason, all of the resource methods
(i.e. API endpoints) return either `JSONDict`, `JSONList`, `None`. In the case
of the latter two, you're on your own once you're inside the structure, but
knowing the wrapper is at least a good start at sanity.

Note that we deviate from the native API a little bit in that the content-type
and response body of `delete_*` methods is not consistent: some return an empty
body, some return `null`, and at least one returns `{}`. Here's the deal: if the
reponse status from a API call is `204`, you will get `None`. This is
[in line with the documentation](https://dev.fitbit.com/build/reference/web-api/troubleshooting-guide/error-messages/#204-no-content).

An area where it's tempting to deviate, but we don't, is in data structures in
the body of the responses. To start, the interns who developed the
[Web API](https://dev.fitbit.com/build/reference/web-api/) were not very
consistent with naming and typing of the API endpoints or the responses. Just a
few examples:

- `create_activity_goals` only allows you to create one goal at a time
- `add_favorite_foods` adds one food at a time, and "add" is only used here.
  It's "create" everywhere else.
- Method names that suggest they would return a list usually don't. They use
  this structure (for example, from
  `activity_timeseries#get_time_series_by_date`)

```json
{
  "activities-steps": [
    {
      "dateTime": "2025-01-29",
      "value": "7434"
    },
    {
      "dateTime": "2025-01-30",
      "value": "4780"
    }
  ]
}
```

This would be a lovely and reliable convention! Except that:

```
get_favorite_activities
get_frequent_activities
get_recent_activity_types
get_favorite_activities
get_frequent_activities
get_recent_activity_types
get_devices
get_food_locales
get_food_units
get_frequent_foods
get_recent_foods
get_spo2_summary_by_interval
```

All return lists. If there is a rhyme or reason for this, I've not found it yet.

## Naming

Methods are named exactly as they appear in the
[Web API Documentation](https://dev.fitbit.com/build/reference/web-api/). When
there are inconsistencies (frequently) the documentation;s URL slug is the
deciding factor. For example, for "Get AZM Time Series by Date"
https://dev.fitbit.com/build/reference/web-api/active-zone-minutes-timeseries/get-azm-timeseries-by-date/,
(which is it--"Time Series" or "timeseries"?) the method in our code will be
`get_azm_timeseries_by_date()`.

## Method Return Types

### ActiveZoneMinutesResource

- `get_azm_timeseries_by_date -> JSONDict`
- `get_azm_timeseries_by_interval -> JSONDict`

### ActivityTimeSeriesResource

- `get_activity_timeseries_by_date -> JSONDict`
- `get_activity_timeseries_by_date_range -> JSONDict`

### ActivityResource

- `create_activity_goals -> JSONDict`
- `create_activity_goal -> JSONDict` (alias for create_activity_goals)
- `create_activity_log -> JSONDict`
- `create_favorite_activity -> Dict[Never, Never]` ??
- `delete_activity_log -> Dict[Never, Never]` ??
- `get_activity_log_list -> JSONDict`
- `delete_favorite_activity -> None`
- `get_activity_goals -> JSONDict`
- `get_daily_activity_summary -> JSONDict`
- `get_activity_type -> JSONDict`
- `get_all_activity_types -> JSONDict`
- `get_favorite_activities -> JSONList`
- `get_frequent_activities -> JSONList`
- `get_recent_activity_types -> JSONList`
- `get_lifetime_stats -> JSONDict`
- `get_activity_tcx -> str` (XML)

### BaseResource

- `_make_request -> JSONType` (gets `cast` as a more specific type when called)

### BodyTimeSeriesResource

- `get_body_timeseries_by_date -> JSONDict`
- `get_body_timeseries_by_date_range -> JSONDict`
- `get_bodyfat_timeseries_by_date -> JSONDict`
- `get_bodyfat_timeseries_by_date_range -> JSONDict`
- `get_weight_timeseries_by_date -> JSONDict`
- `get_weight_timeseries_by_date_range -> JSONDict`

### BodyResource

- `create_bodyfat_goal -> JSONDict`
- `create_bodyfat_log -> JSONDict`
- `create_weight_goal -> JSONDict`
- `create_weight_log -> JSONDict`
- `delete_bodyfat_log -> None`
- `delete_weight_log -> None`
- `get_body_goals -> JSONDict`
- `get_bodyfat_log -> JSONDict`
- `get_weight_logs -> JSONDict`

### BreathingRateResource

- `get_breathing_rate_summary_by_date -> JSONDict`
- `get_breathing_rate_summary_by_interval -> JSONDict`

### CardioFitnessScoreResource

- `get_vo2_max_summary_by_date -> JSONDict`
- `get_vo2_max_summary_by_interval -> JSONDict`

### DeviceResource

- `get_devices -> JSONList`
- `create_alarm` (raises `NotImplementedError`)
- `delete_alarm` (raises `NotImplementedError`)
- `get_alarm` (raises `NotImplementedError`)
- `update_alarm` (raises `NotImplementedError`)

### ElectrocardiogramResource

- `get_ecg_log_list -> JSONDict`

### FriendsResource

- `get_friends -> JSONDict`
- `get_friends_leaderboard -> JSONDict`

### HeartrateTimeSeriesResource

- `get_heartrate_timeseries_by_date -> JSONDict`
- `get_heartrate_timeseries_by_date_range -> JSONDict`

### HeartrateVariabilityResource

- `get_hrv_summary_by_date -> JSONDict`
- `get_hrv_summary_by_interval -> JSONDict`

### IntradayResource

- `get_azm_intraday_by_date -> JSONDict`
- `get_azm_intraday_by_interval -> JSONDict`
- `get_activity_intraday_by_date -> JSONDict`
- `get_activity_intraday_by_interval -> JSONDict`
- `get_breathing_rate_intraday_by_date -> JSONDict`
- `get_breathing_rate_intraday_by_interval -> JSONDict`
- `get_heartrate_intraday_by_date -> JSONDict`
- `get_heartrate_intraday_by_interval -> JSONDict`
- `get_hrv_intraday_by_date -> JSONDict`
- `get_hrv_intraday_by_interval -> JSONDict`
- `get_spo2_intraday_by_date -> JSONDict`
- `get_spo2_intraday_by_interval -> JSONDict`

### IrregularRhythmNotificationsResource

- `get_irn_alerts_list -> JSONDict`
- `get_irn_profile -> JSONDict`

### NutritionTimeSeriesResource

- `get_nutrition_timeseries_by_date -> JSONDict`
- `get_nutrition_timeseries_by_date_range -> JSONDict`

### NutritionResource

- `add_favorite_foods -> None`
- `add_favorite_food -> None` (alias for add_favorite_foods)
- `create_favorite_food -> None` (alias for add_favorite_foods)
- `create_food -> JSONDict`
- `create_food_log -> JSONDict`
- `create_food_goal -> JSONDict`
- `create_meal -> JSONDict`
- `create_water_goal -> JSONDict`
- `create_water_log -> JSONDict`
- `delete_custom_food -> None`
- `delete_favorite_foods -> None`
- `delete_favorite_food -> None` (alias for delete_favorite_foods)
- `delete_food_log -> None`
- `delete_meal -> None`
- `delete_water_log -> None`
- `get_food -> JSONDict`
- `get_food_goals -> JSONDict`
- `get_food_log -> JSONDict`
- `get_food_locales -> JSONList`
- `get_food_units -> JSONList`
- `get_frequent_foods -> JSONList`
- `get_recent_foods -> JSONList`
- `get_favorite_foods -> JSONDict`
- `get_meal -> JSONDict`
- `get_meals -> JSONDict`
- `get_water_goal -> JSONDict`
- `get_water_log -> JSONDict`
- `search_foods -> JSONDict`
- `update_food_log -> JSONDict`
- `update_meal -> JSONDict`
- `update_water_log -> JSONDict`

### SleepResource

- `create_sleep_goals -> JSONDict`
- `create_sleep_goal -> JSONDict` (alias for create_sleep_goals)
- `create_sleep_log -> JSONDict`
- `delete_sleep_log -> None`
- `get_sleep_goals -> JSONDict`
- `get_sleep_goal -> JSONDict` (alias for get_sleep_goals)
- `get_sleep_log_by_date -> JSONDict`
- `get_sleep_log_by_date_range -> JSONDict`
- `get_sleep_log_list -> JSONDict`

### SpO2Resource

- `get_spo2_summary_by_date -> JSONDict`
- `get_spo2_summary_by_interval -> JSONList`

### SubscriptionResource

- `get_subscription_list -> JSONDict`
- `create_subscription` (raises `NotImplementedError`)
- `delete_subscription` (raises `NotImplementedError`)

### TemperatureResource

- `get_temperature_core_summary_by_date -> JSONDict`
- `get_temperature_core_summary_by_interval -> JSONDict`
- `get_temperature_skin_summary_by_date -> JSONDict`
- `get_temperature_skin_summary_by_interval -> JSONDict`

### UserResource

- `get_profile -> JSONDict`
- `update_profile -> JSONDict`
- `get_badges -> JSONDict`
