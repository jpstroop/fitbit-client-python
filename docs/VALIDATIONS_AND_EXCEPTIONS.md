# Input Validation and Error Handling

Many method parameter arguments are validated **before making any API
requests**. The aim is to encapsulate the HTTP API as much as possible and raise
more helpful exceptions before a bad request is executed. This approach:

- Preserves your API rate limits by catching errors locally
- Provides more specific and helpful error messages
- Simplifies debugging by clearly separating client-side validation issues from
  API response issues

Understanding these validations and the exceptions that are raised by them (and
elsewhere) will help you use this library correctly and efficiently.

## Input Validation

### Date Formats

All dates must be in one of these formats:

- YYYY-MM-DD (e.g., "2024-02-20")
- "today" (special keyword for current date)

Example:

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

### Date Ranges

When using endpoints that accept date ranges:

- start_date must be before or equal to end_date
- Maximum range varies by endpoint:
  - Body weight logs: 31 days
  - Sleep logs: 100 days
  - Activity data: 31 days
  - General data: 1095 days (approximately 3 years)

Example:

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

### Enumerated Values

The library provides enums for many parameters. Using these enums ensures valid
values:

```python
from fitbit_client.resources.constants import Period, ActivityGoalType

# Valid - using provided enum
client.activity.get_activity_timeseries_by_date(
    resource_path=ActivityTimeSeriesPath.STEPS,
    date="today",
    period=Period.ONE_WEEK
)
```

### Required Parameters

Some methods require specific parameter combinations that can be tricky to get
right. For example, creating a food log requires either a `food_id`, or
`food_name` AND `calories`.

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

# Invalid - only provided food_name without calories
try:
    client.nutrition.create_food_log(
        date="2024-02-20",
        meal_type_id=MealType.BREAKFAST,
        unit_id=1,
        amount=1.0,
        food_name="My Custom Food"
    )
except ValidationException as e:
    print(e.message)
    # Output: Must provide either food_id or (food_name and calories)
```

### Numeric Limits

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

# Invalid - Duration must be positive
try:
    client.activity.create_activity_log(
        activity_id=12345,
        duration_millis=-60000,  # -1 minute
        start_time="12:00",
        date="2024-02-20"
    )
except ValidationException as e:
    print(e.message)
    # Output: Duration must be positive
```

## Exception Handling

There are many custom exceptions. When validation fails or other errors occur,
the library raises specific exceptions that help identify the problem.

### Using Custom Validation Exceptions

Client validation exceptions (`ClientValidationException` and its subclasses)
are raised *before* any API call is made. This means:

1. They reflect problems with your input parameters that can be detected locally
2. No network requests have been initiated when these exceptions occur
3. They help you fix issues before consuming API rate limits

This is in contrast to API exceptions (`FitbitAPIException` and its subclasses),
which are raised in response to errors returned by the Fitbit API after a
network request has been made.

When using this library, you'll want to catch the specific exception types for
proper error handling:

```python
from fitbit_client.exceptions import ParameterValidationException, MissingParameterException

try:
    # When parameters might be missing
    client.nutrition.create_food_goal(calories=None, intensity=None)
except MissingParameterException as e:
    print(f"Missing parameter: {e.message}")

try:
    # When parameters might be invalid
    client.sleep.create_sleep_goals(min_duration=-10)
except ParameterValidationException as e:
    print(f"Invalid parameter value for {e.field_name}: {e.message}")
```

You can also catch the base class for all client validation exceptions:

```python
from fitbit_client.exceptions import ClientValidationException

try:
    client.activity.create_activity_log(duration_millis=-100, start_time="12:00", date="2024-02-20")
except ClientValidationException as e:
    print(f"Validation error: {e.message}")
```

### ValidationException

Raised when input parameters do not meet requirements:

```python
try:
    # Value must be positive
    client.activity.create_activity_goal(
        period=ActivityGoalPeriod.DAILY,
        type=ActivityGoalType.STEPS,
        value=-100
    )
except ValidationException as e:
    print(f"Field '{e.field_name}' invalid: {e.message}")
    # Output: Field 'value' invalid: Goal value must be positive
```

### InvalidDateException

Raised when a date format is invalid:

```python
try:
    client.activity.get_daily_activity_summary("01-01-2024")
except InvalidDateException as e:
    print(e.message)
    # Output: Invalid date format. Use YYYY-MM-DD or 'today'
```

### InvalidDateRangeException

Raised when date ranges are invalid or exceed limits:

```python
try:
    client.sleep.get_sleep_log_by_date_range(
        start_date="2024-01-01",
        end_date="2023-12-31"  # End date before start date
    )
except InvalidDateRangeException as e:
    print(e.message)
```

### AuthorizationException

Raised for authentication or authorization issues:

```python
try:
    client.activity.get_lifetime_stats()
except AuthorizationException as e:
    print(f"Auth error ({e.status_code}): {e.message}")
```

### RateLimitExceededException

Raised when you've exceeded Fitbit's API rate limits:

```python
try:
    client.activity.get_daily_activity_summary("today")
except RateLimitExceededException as e:
    print(f"Rate limit exceeded: {e.message}")
    # Implement appropriate backoff strategy
```

### Exception Properties

API exceptions (`FitbitAPIException` and its subclasses) provide these
properties:

- `message`: Human-readable error description
- `status_code`: HTTP status code (if applicable)
- `error_type`: Type of error from the API
- `field_name`: Name of the invalid field (for validation errors)

Validation exceptions (`ClientValidationException` and its subclasses) provide:

- `message`: Human-readable error description
- `field_name`: Name of the invalid field (for validation errors)

Specific validation exception subclasses provide additional properties:

- `InvalidDateException`: Adds `date_str` property with the invalid date string
- `InvalidDateRangeException`: Adds `start_date`, `end_date`, `max_days`, and
  `resource_name` properties
- `IntradayValidationException`: Adds `allowed_values` and `resource_name`
  properties
- `ParameterValidationException`: Used for invalid parameter values (e.g.,
  negative where positive is required)
- `MissingParameterException`: Used when required parameters are missing or
  parameter combinations are invalid

### Exception Hierarchy:

```
Exception
├── ValueError
│   └── ClientValidationException             # Superclass for validations that take place before 
│       │                                     #   making a request
│       ├── InvalidDateException              # Raised when a date string is not in the correct 
│       │                                     #   format or not a valid calendar date
│       ├── InvalidDateRangeException         # Raised when a date range is invalid (e.g., end is 
│       │                                     #   before start, exceeds max days)
│       ├── PaginationException               # Raised when pagination parameters are invalid
│       ├── IntradayValidationException       # Raised when intraday request parameters are invalid
│       ├── ParameterValidationException      # Raised when a parameter value is invalid
│       │                                     #   (e.g., negative when positive required)
│       └── MissingParameterException         # Raised when required parameters are missing or
│                                             #   parameter combinations are invalid
│
└── FitbitAPIException                        # Base exception for all Fitbit API errors
    │
    ├── OAuthException                        # Superclass for all authentication flow exceptions
    │   ├── ExpiredTokenException             # Raised when the OAuth token has expired
    │   ├── InvalidGrantException             # Raised when the grant_type value is invalid
    │   ├── InvalidTokenException             # Raised when the OAuth token is invalid
    │   └── InvalidClientException            # Raised when the client_id is invalid
    │
    └── RequestException                      # Superclass for all API request exceptions
        ├── InvalidRequestException           # Raised when the request syntax is invalid
        ├── AuthorizationException            # Raised when there are authorization-related errors
        ├── InsufficientPermissionsException  # Raised when the application has insufficient permissions
        ├── InsufficientScopeException        # Raised when the application is missing a required scope
        ├── NotFoundException                 # Raised when the requested resource does not exist
        ├── RateLimitExceededException        # Raised when the application hits rate limiting quotas
        ├── SystemException                   # Raised when there is a system-level failure
        └── ValidationException               # Raised when a request parameter is invalid or missing
```

## Debugging

Every method accepts a `debug` parameter that prints the equivalent cURL
command:

```python
client.activity.get_daily_activity_summary(
    date="today",
    debug=True
)
# Prints:
# curl -X GET -H "Authorization: Bearer <token>" ...
```

This can help troubleshoot API interactions by showing the exact request being
made.
