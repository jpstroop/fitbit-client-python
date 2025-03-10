# Input Validation

The library performs thorough validation of input parameters **before making any
API requests**. This approach:

- Preserves your API rate limits by catching errors locally
- Provides more specific and helpful error messages
- Simplifies debugging by separating client-side validation from API issues

## Date Formats

All dates must be in one of these formats:

- YYYY-MM-DD (e.g., "2024-02-20")
- "today" (special keyword for current date)

```python
# Valid dates
client.activity.get_daily_activity_summary("2024-02-20")
client.activity.get_daily_activity_summary("today")

# Invalid - will raise InvalidDateException 
try:
    client.activity.get_daily_activity_summary("02-20-2024")
except InvalidDateException as e:
    print(e.message)
    # Output: Invalid date format. Use YYYY-MM-DD or 'today'
```

## Date Ranges

When using endpoints that accept date ranges:

- `start_date` must be before or equal to `end_date`
- Maximum range varies by endpoint:
  - Body weight logs: 31 days
  - Sleep logs: 100 days
  - Activity data: 31 days
  - General data: 1095 days (approximately 3 years)

```python
# Valid range within limits
client.sleep.get_sleep_log_by_date_range(
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Invalid - exceeds sleep data 100 day limit
try:
    client.sleep.get_sleep_log_by_date_range(
        start_date="2024-01-01",
        end_date="2024-12-31"
    )
except InvalidDateRangeException as e:
    print(e.message)
    # Output: Date range cannot exceed 100 days for sleep time series
```

## Enumerated Values

The library provides enums for many parameters to ensure valid values:

```python
from fitbit_client.resources._constants import Period, ActivityGoalType

# Valid - using provided enum
client.activity.get_activity_timeseries_by_date(
    resource_path=ActivityTimeSeriesPath.STEPS,
    date="today",
    period=Period.ONE_WEEK
)

# Invalid - will raise ValidationException
try:
    client.activity.get_activity_timeseries_by_date(
        resource_path=ActivityTimeSeriesPath.STEPS,
        date="today",
        period="invalid_period"
    )
except ValidationException as e:
    print(e.message)
    # Output: Invalid period value. Use one of: 1d, 7d, 30d, 1w, 1m, 3m, 6m, 1y, max
```

## Required Parameters

Some methods require specific parameter combinations:

```python
# Valid - using food_id
client.nutrition.create_food_log(
    date="2024-02-20",
    meal_type_id=MealType.BREAKFAST,
    unit_id=1,
    amount=1.0,
    food_id=12345  # Option 1
)

# Valid - using food_name and calories
client.nutrition.create_food_log(
    date="2024-02-20",
    meal_type_id=MealType.BREAKFAST,
    unit_id=1,
    amount=1.0,
    food_name="My Custom Food",  # Option 2
    calories=200                 # Option 2
)

# Invalid - missing both food_id and (food_name, calories)
try:
    client.nutrition.create_food_log(
        date="2024-02-20",
        meal_type_id=MealType.BREAKFAST,
        unit_id=1,
        amount=1.0
    )
except ValidationException as e:
    print(e.message)
    # Output: Must provide either food_id or (food_name and calories)
```

## Numeric Limits

Many endpoints enforce numeric limits:

```python
# Invalid - Cannot request more than 100 records
try:
    client.get_activity_log_list(limit=200)
except ValidationException as e:
    print(e.message)
    # Output: Maximum limit is 100 records

# Invalid - Goal value must be positive
try:
    client.activity.create_activity_goals(
        period=ActivityGoalPeriod.DAILY,
        type=ActivityGoalType.STEPS,
        value=-1000
    )
except ValidationException as e:
    print(e.message)
    # Output: Goal value must be positive
```

## Pagination Parameters

When using endpoints with pagination:

- Only one of `offset`/`limit` or `before_date`/`after_date`/`sort` can be used
- `sort` must be consistent with the date parameter used (ascending with
  `after_date`, descending with `before_date`)
- Maximum records per request is typically limited (often 100)

```python
# Valid - using offset/limit pagination
client.activity.get_activity_log_list(offset=0, limit=10)

# Valid - using date-based pagination
client.activity.get_activity_log_list(
    after_date="2024-01-01",
    sort="asc"
)

# Invalid - mixing pagination methods
try:
    client.activity.get_activity_log_list(
        offset=0, 
        limit=10,
        after_date="2024-01-01"
    )
except PaginationException as e:
    print(e.message)
    # Output: Cannot mix offset/limit with date-based pagination
```

## Custom and Combined Validation

Some endpoints have custom validation requirements:

```python
# Custom validation for food log creation
try:
    client.nutrition.create_food_log(
        date="2024-02-20",
        meal_type_id=MealType.BREAKFAST,
        food_name="Test Food",
        # Missing calories!
        unit_id=1,
        amount=1.0
    )
except MissingParameterException as e:
    print(e.message)
    # Output: When using food_name, calories is required
```

## Validation Implementation

For a complete understanding of the exception system that powers these
validations, see [ERROR_HANDLING.md](ERROR_HANDLING.md).
