# API Method Naming Conventions

## Naming Principles

The method names in this library are designed to align with the official Fitbit
Web API Documentation. When there are inconsistencies in the official
documentation, we prioritize the URL slug. For example, if the documentation
page title says "Get **Time Series** by Date" but the URL is
".../get-azm-timeseries-by-date/", our method will be named
`get_azm_timeseries_by_date()`. (not `get_azm_time_series_by_date()`).

This approach ensures consistent naming throughout the library and makes methods
easier to find based on the official documentation.

## Inconsistencies in the API

The Fitbit API contains several inconsistencies, which our method names and
implementation dutifully reflect. Understanding these inconsistencies can help
you navigate the API more effectively:

### Method Name vs. Functionality Inconsistencies

- `create_activity_goals` creates only one goal at a time, despite the plural
  name
- `add_favorite_foods` adds one food at a time, while all other creation methods
  start with "create".
- `get_sleep_goals` returns a single goal, not multiple goals
- Additionally, some pluralized methods return lists, while others return
  dictionaries containing lists

For user convenience, these inconsistencies have aliases:

- (`alias` -> `target`)
- `create_activity_goal` -> `create_activity_goals`
- `add_favorite_food` -> `add_favorite_foods`
- `create_favorite_food` -> `add_favorite_foods`
- `delete_favorite_food` -> `delete_favorite_foods`
- `create_sleep_goal` -> `create_sleep_goals`
- `get_sleep_goal` -> `get_sleep_goals`

These aliases help accommodate different expectations and ensure backward
compatibility.

### Response Structure Inconsistencies

The structure of API responses varies widely across endpoints:

```python
# Some endpoints return arrays directly
activities = client.get_frequent_activities()
# activities is a List[Dict[str, Any]] (array of activity objects)

# Others wrap arrays in a parent object with a named property
sleep_logs = client.get_sleep_log_by_date(date="2025-01-01")
# sleep_logs is a Dict[str, Any] with a "sleep" property containing the array

# Some endpoints use plural property names for lists
weight_logs = client.get_weight_logs(date="2025-01-01")
# weight_logs["weight"] is the list of weight logs

# Others use singular property names for lists
food_logs = client.get_food_log(date="2025-01-01")
# food_logs["foods"] is the list of food logs
```

### Error Response Inconsistencies

Error responses can also vary in structure:

```python
try:
    # Some validation errors include field names
    client.create_food_log(food_id="invalid", amount=100, meal_type_id=1)
except ValidationException as e:
    print(e.field_name)  # Might be "foodId"

try:
    # Other validation errors omit field names
    client.get_activity_tcx(log_id="invalid")
except InvalidRequestException as e:
    print(e.field_name)  # Might be None
```

Our library handles these inconsistencies internally to provide a unified
experience, but it's helpful to be aware of them when working with the raw API
responses.

## Resource Structure

The client organizes API endpoints into logical resource classes, each
representing a different section of the Fitbit API. For a complete list of all
methods and their return types, see
[TYPES.md](TYPES.md#method-return-types-reference).
