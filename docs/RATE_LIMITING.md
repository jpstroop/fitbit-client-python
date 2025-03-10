# Rate Limiting

The Fitbit API enforces rate limits to prevent overuse. When you exceed these
limits, the API returns a `429 Too Many Requests` error. We attempt to include
retry mechanisms to handle rate limiting gracefully.

## How It Works

When a rate limit is encountered, the client will:

1. Log a warning message with details about the rate limit
2. Wait for an appropriate amount of time using exponential backoff
3. Automatically retry the request (up to a configurable maximm)
4. Either return the successful response or raise an exceptione after exhausting
   retries

All of this should happen transparently and without manual intervention.

## Configuration

Configure rate limiting behavior when creating the client:

```python
from fitbit_client import FitbitClient

client = FitbitClient(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="https://localhost:8080",
    
    # Rate limiting options (all optional)
    max_retries=5,                # Maximum retry attempts (default: 3)
    retry_after_seconds=30,       # Base wait time in seconds (default: 60)
    retry_backoff_factor=2.0      # Multiplier for successive waits (default: 1.5)
)
```

## Exponential Backoff

The wait time between retries increases exponentially to avoid overwhelming the
API. The formula is:

```
retry_time = retry_after_seconds * (retry_backoff_factor ^ retry_count)
```

With the default settings:

- First retry: Wait 60 seconds
- Second retry: Wait 90 seconds (60 * 1.5)
- Third retry: Wait 135 seconds (60 * 1.5²)

## Fitbit API Rate Limits

The Fitbit API has different rate limits for different endpoints:

- **User-level rate limits**: Up to 150 API calls per hour per user
- **Client-level rate limits**: For applications with many users

Refer to the
[Fitbit API Rate Limits documentation](https://dev.fitbit.com/build/reference/web-api/developer-guide/application-design/#Rate-Limits)
for the most current information.

## Logging

Rate limit events are logged to the standard application logger. To capture
these logs:

```python
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Use the client
client = FitbitClient(...)
```

You'll see log messages like:

```
WARNING:fitbit_client.SleepResource:Rate limit exceeded for get_sleep_log_list to sleep/list.json. Retrying in 60 seconds. (2 retries remaining)
```

## Handling Unrecoverable Rate Limits

If all retry attempts are exhausted, the client will raise a
`RateLimitExceededException`. You can catch this exception to implement your own
fallback logic:

```python
from fitbit_client import FitbitClient
from fitbit_client.exceptions import RateLimitExceededException

client = FitbitClient(...)

try:
    # Make API request
    data = client.get_activity_log_list(before_date="2025-01-01")
    # Process data
except RateLimitExceededException as e:
    # Handle unrecoverable rate limit
    print(f"Rate limit exceeded even after retries: {e}")
    # Implement fallback logic
```
