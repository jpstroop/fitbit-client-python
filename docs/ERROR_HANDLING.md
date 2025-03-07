# Exception Handling

The library implements a comprehensive exception system to help you handle
errors effectively. Understanding these exceptions will help you write more
robust code.

## Exception Hierarchy

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

## Client Validation Exceptions

Client validation exceptions (`ClientValidationException` and its subclasses)
are raised *before* any API call is made:

1. They reflect problems with your input parameters that can be detected locally
2. No network requests have been initiated when these exceptions occur
3. They help you fix issues before consuming API rate limits

```python
from fitbit_client.exceptions import InvalidDateException, InvalidDateRangeException

try:
    client.sleep.get_sleep_log_by_date_range(
        start_date="2024-01-01",
        end_date="2023-12-31"  # End date before start date
    )
except InvalidDateRangeException as e:
    print(f"Date range error: {e.message}")
    print(f"Start date: {e.start_date}, End date: {e.end_date}")
    print(f"Resource: {e.resource_name}, Max days: {e.max_days}")
```

### Common Client Validation Exceptions

- **InvalidDateException**: Raised when a date string is not valid
- **InvalidDateRangeException**: Raised when a date range is invalid
- **ParameterValidationException**: Raised when a parameter value is invalid
- **MissingParameterException**: Raised when required parameters are missing
- **PaginationException**: Raised when pagination parameters are invalid
- **IntradayValidationException**: Raised when intraday request parameters are
  invalid

## API Exceptions

API exceptions (`FitbitAPIException` and its subclasses) are raised in response
to errors returned by the Fitbit API:

```python
from fitbit_client.exceptions import AuthorizationException, RateLimitExceededException

try:
    client.activity.get_lifetime_stats()
except AuthorizationException as e:
    print(f"Auth error ({e.status_code}): {e.message}")
    # Handle authentication error (e.g., refresh token, prompt for re-auth)
except RateLimitExceededException as e:
    retry_after = int(e.headers.get("Retry-After", 60))
    print(f"Rate limit exceeded. Retry after {retry_after} seconds")
    # Implement backoff strategy
```

### Common API Exceptions

- **AuthorizationException**: Authentication or authorization issues
- **InvalidRequestException**: Invalid request syntax or parameters
- **RateLimitExceededException**: API rate limits exceeded
- **NotFoundException**: Requested resource doesn't exist
- **SystemException**: Fitbit API server-side errors

## Exception Properties

### Client Validation Exceptions

All client validation exceptions have these properties:

- `message`: Human-readable error description
- `field_name`: Name of the invalid field (if applicable)

Specific validation exception types add additional properties:

- **InvalidDateException**: `date_str` (the invalid date string)
- **InvalidDateRangeException**: `start_date`, `end_date`, `max_days`,
  `resource_name`
- **IntradayValidationException**: `allowed_values`, `resource_name`

### API Exceptions

All API exceptions have these properties:

- `message`: Human-readable error description
- `status_code`: HTTP status code (if applicable)
- `error_type`: Type of error from the API
- `field_name`: Name of the invalid field (for validation errors)
- `headers`: Response headers (useful for rate limiting info)

## Usage Patterns

### Catching Specific Exceptions

Target specific exceptions for tailored error handling:

```python
try:
    client.activity.create_activity_goals(
        period=ActivityGoalPeriod.DAILY,
        type=ActivityGoalType.STEPS,
        value=-1000
    )
except ParameterValidationException as e:
    print(f"Invalid value for {e.field_name}: {e.message}")
except AuthorizationException as e:
    print(f"Authorization error: {e.message}")
except RateLimitExceededException as e:
    print(f"Rate limit error: {e.message}")
```

### Catching Base Exception Classes

Catch base classes to handle related exceptions together:

```python
try:
    client.activity.get_daily_activity_summary("today")
except ClientValidationException as e:
    print(f"Invalid input: {e.message}")  # Catches all input validation errors
except OAuthException as e:
    print(f"OAuth error: {e.message}")  # Catches all OAuth-related errors
except FitbitAPIException as e:
    print(f"API error: {e.message}")  # Catches all other API errors
```

### Handling OAuth-Specific Exceptions

OAuth errors require special handling. Here's how to handle different OAuth
exception subtypes:

```python
from fitbit_client.exceptions import ExpiredTokenException, InvalidTokenException
from fitbit_client.exceptions import InvalidClientException, InvalidGrantException

try:
    # Make an API call that requires authentication
    client.get_profile()
except ExpiredTokenException as e:
    # Token has expired but couldn't be auto-refreshed
    print(f"Token expired: {e.message}")
    # Attempt to re-authenticate
    client.authenticate()
except InvalidTokenException as e:
    # Token is invalid (e.g., revoked by user)
    print(f"Token invalid: {e.message}")
    # Re-authenticate from scratch
    client.authenticate()
except InvalidClientException as e:
    # Client credentials are incorrect
    print(f"Client credentials error: {e.message}")
    # Check client_id and client_secret
except InvalidGrantException as e:
    # Refresh token is invalid
    print(f"Invalid refresh token: {e.message}")
    # Re-authenticate to get a new refresh token
    client.authenticate()
```

## Token Refresh Strategies

The client automatically handles token refresh when tokens expire. However, you
may want to implement custom token refresh strategies for your application.

### Automatic Token Refresh

By default, the client refreshes tokens automatically:

1. When initializing the client with cached tokens
2. During API calls when a token expires
3. When explicitly calling a method that requires authentication

```python
# Tokens are automatically refreshed
client = FitbitClient(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="https://localhost:8080",
    token_cache_path="/path/to/tokens.json"  # Enable persistent token caching
)

# If cached tokens exist and are valid or can be refreshed, no browser prompt occurs
client.authenticate()

# If the token expires during this call, it will be refreshed automatically
client.get_profile()
```

### Handling Failed Token Refresh

When automatic token refresh fails, the client raises an appropriate OAuth
exception. Here's a complete error handling pattern:

```python
from fitbit_client.exceptions import OAuthException, ExpiredTokenException

try:
    result = client.get_profile()
    # Process result normally
except ExpiredTokenException:
    # Token expired and auto-refresh failed
    try:
        # Try to authenticate again
        client.authenticate()
        # Retry the original request
        result = client.get_profile()
    except OAuthException as oauth_error:
        # Handle authentication failure (e.g., user closed browser window)
        print(f"Authentication failed: {oauth_error.message}")
        # Log the user out or provide error message
except OAuthException as e:
    # Handle other OAuth errors
    print(f"OAuth error: {e.message}")
```

## Debugging APIs

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

This helps troubleshoot API interactions by showing the exact request being
made.
