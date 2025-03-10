# Rate Limiting

See
[Rate Limits](https://dev.fitbit.com/build/reference/web-api/developer-guide/application-design/#Rate-Limits)

The Fitbit API enforces rate limits to prevent overuse. The API has a rate limit
of 150 API requests per hour for each user who has consented to share their
data. When you exceed these limits, the API returns a `429 Too Many Requests`
error.

## Fitbit API Rate Limits

According to the official Fitbit API documentation:

- **User-level rate limit**: 150 API requests per hour per user
- **Reset time**: Approximately at the top of each hour
- **Response headers**:
  - `Fitbit-Rate-Limit-Limit`: The quota number of calls
  - `Fitbit-Rate-Limit-Remaining`: The number of calls remaining
  - `Fitbit-Rate-Limit-Reset`: The number of seconds until the rate limit resets

When you hit the rate limit, the API returns an HTTP 429 response with the
`Fitbit-Rate-Limit-Reset` header indicating the number of seconds until the
limit resets.

## Automatic Retry Mechanism

When a rate limit is encountered, the client will:

1. Log the rate limit information (limit, remaining calls, reset time)
2. Wait for the time specified in the `Fitbit-Rate-Limit-Reset` header
3. Automatically retry the request (up to a configurable maximum)
4. Either return the successful response or raise an exception after exhausting
   retries

All of this happens transparently without manual intervention.

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
    retry_after_seconds=60,       # Base wait time if headers missing (default: 60)
    retry_backoff_factor=1.5      # Multiplier for successive waits (default: 1.5)
)
```

## Retry Strategy

The client uses the following strategy for retries:

1. Use the `Fitbit-Rate-Limit-Reset` header if available

2. Fall back to the standard `Retry-After` header if available

3. If neither header is present, use exponential backoff with the formula:

   ```
   retry_time = retry_after_seconds * (retry_backoff_factor ^ retry_count)
   ```

With example settings of 5 retries and no headers:

- First retry: Wait 60 seconds (base time)
- Second retry: Wait 90 seconds (60 * 1.5¹)
- Third retry: Wait 135 seconds (60 * 1.5²)
- Fourth retry: Wait 202.5 seconds (60 * 1.5³)
- Fifth retry: Wait 303.75 seconds (60 * 1.5⁴)

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
WARNING:fitbit_client.SleepResource:Rate limit exceeded for get_sleep_log_list to sleep/list.json. [Rate Limit: 0/150] Retrying in 600 seconds. (4 retries remaining)
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
    print(f"Will reset in {e.rate_limit_reset} seconds")
    # Implement fallback logic
```

## Rate Limit Headers

The `RateLimitExceededException` includes properties from the Fitbit rate limit
headers:

```python
except RateLimitExceededException as e:
    print(f"Rate limit: {e.rate_limit}")              # Total allowed calls (150)
    print(f"Remaining: {e.rate_limit_remaining}")     # Remaining calls before limit
    print(f"Reset in: {e.rate_limit_reset} seconds")  # Seconds until limit reset
```

These can be used to implement more sophisticated retry or backoff strategies in
your application.

## Advanced Usage

You can implement custom strategies by combining rate limit information with
your own timing logic:

```python
from datetime import datetime, timedelta
from time import sleep

try:
    client.get_daily_activity_summary(date="today")
except RateLimitExceededException as e:
    # Calculate next reset time (typically the top of the next hour)
    reset_time = datetime.now() + timedelta(seconds=e.rate_limit_reset)
    print(f"Rate limit reached. Pausing until {reset_time.strftime('%H:%M:%S')}")
    
    # Wait until reset time plus a small buffer
    wait_seconds = e.rate_limit_reset + 5
    sleep(wait_seconds)
    
    # Try again after waiting
    client.get_daily_activity_summary(date="today")
```
