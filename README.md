# Python API Client for Fitbit™

[![CI](https://github.com/jpstroop/fitbit-client-python/actions/workflows/ci.yml/badge.svg)](https://github.com/jpstroop/fitbit-client-python/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/jpstroop/fitbit-client-python/graph/badge.svg?token=DM0JD8VKZ4)](https://codecov.io/gh/jpstroop/fitbit-client-python)

[![Tested with Pytest](https://img.shields.io/badge/Pytest-tested-0A9EDC?logo=pytest&logoColor=#0A9EDC)](https://docs.pytest.org/en/stable/)
[![Type checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Doc style: MDformat](https://img.shields.io/badge/doc_style-mdformat-1c55ff?style=flat)](https://mdformat.readthedocs.io/en/stable/)

[![PyPy 3.11](https://img.shields.io/badge/pypy-3.11-4bb2c5?logo=pypy&logoColor=#4bb2c5)](https://doc.pypy.org/en/latest/release-v7.3.17.html)
[![Python 3.11](https://img.shields.io/badge/python-3.11-1e405d?logo=python&logoColor=#3776AB)](https://www.python.org/downloads/release/python-3110/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-1e405d?logo=python&logoColor=#3776AB)](https://www.python.org/downloads/release/python-3120/)
[![Python 3.13](https://img.shields.io/badge/python-3.13-1e405d?logo=python&logoColor=#3776AB)](https://www.python.org/downloads/release/python-3130/)

[![Linux](https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black)](#)
[![macOS](https://img.shields.io/badge/macOS-000000?logo=apple&logoColor=F0F0F0)](#)
[![Windows](https://custom-icon-badges.demolab.com/badge/Windows-0078D6?logo=windows11&logoColor=white)](#)

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

A fully-typed Python client for interacting with the Fitbit API, featuring
OAuth2 PKCE authentication and resource-based API interactions.

## Installation

Requires Python 3.11 or later

Once published, install like this:

```bash
pdm add fitbit-client-python # or your dependency manager of choice
```

For now, you can
[use it from Github](https://pdm-project.org/latest/usage/dependency/#vcs-dependencies).

## Quick Start

```python
from fitbit_client import FitbitClient
from json import dumps

# Initialize client
client = FitbitClient(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="https://localhost:8080"
)

try:
    # Authenticate (opens browser automatically)
    client.authenticate()
    
    # Make a request (e.g., get user profile)
    # You can access resources directly:
    profile = client.user.get_profile()
    # Or use method aliases for shorter syntax:
    profile = client.get_profile()
    print(dumps(profile, indent=2))
    
except Exception as e:
    print(f"Error: {str(e)}")
```

The response will always be the body of the API response, and is almost always a
`JSONDict`, `JSONList` or `None`. `nutrition.get_activity_tcx` is the exception.
It returns XML (as a `str`).

## Method Aliases

All API methods are available directly from the client instance. This means you
can use:

```python
# Short form with method aliases
client.get_profile()
client.get_daily_activity_summary(date="2025-03-06")
client.get_sleep_log_by_date(date="2025-03-06")
```

Instead of the longer form:

```python
# Standard resource access
client.user.get_profile()
client.activity.get_daily_activity_summary(date="2025-03-06")
client.sleep.get_sleep_log_by_date(date="2025-03-06")
```

Both approaches are equivalent, but aliases provide a more concise syntax.

## Authentication

Authentication wses a local callback server to handle the OAuth2 flow:

```python
client = FitbitClient(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="YOUR_REGISTERED_REDIRECT_URI",
    token_cache_path="/tmp/fb_tokens.json" 
)

# This will open browser and handle callback automatically:
client.authenticate()
```

You can also load your credentials from a JSON file, which is useful for keeping
secrets out of your code:

```python
from json import load
from fitbit_client import FitbitClient

# Load credentials from a JSON file
with open("secrets.json") as f:
    secrets = load(f)

# Initialize Fitbit OAuth2 flow and get a client
client = FitbitClient(**secrets)

# Authenticate as usual
client.authenticate()
```

Where secrets.json contains:

```json
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "redirect_uri": "https://localhost:8080"
}
```

Using this strategy, you can initialize the client with several additional
parameter arguments (such as [Rate Limiting](#rate-limiting) and language/locale
options; see the [FitbitClient](fitbit_client/client.py) initializer). Perhaps
the most useful of these is the `token_cache_path`:

```json
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "redirect_uri": "https://localhost:8080",
  "token_cache_path": "/tmp/tokens.json"
}
```

The `token_cache_path` parameter allows you to persist authentication tokens
between sessions. If provided, the client will:

1. Load existing tokens from this file if available (avoiding re-authentication)
2. Save new or refreshed tokens to this file automatically
3. Handle token refresh when expired tokens are detected

## Setting Up Your Fitbit App

1. Go to dev.fitbit.com and create a new application
2. Set OAuth 2.0 Application Type to "Personal" (or other types, if you know
   what you're doing)
3. Set Callback URL to "https://localhost:8080" (or your preferred local URL)
4. Copy your Client ID and Client Secret

## Pagination

Some Fitbit API endpoints support pagination for large result sets. You can work
with paginated endpoints in two ways:

```python
# Standard way - get a single page of results
sleep_logs = client.get_sleep_log_list(before_date="2025-01-01")

# Iterator way - get an iterator that fetches all pages automatically
for page in client.get_sleep_log_list(before_date="2025-01-01", as_iterator=True):
    for sleep_entry in page["sleep"]:
        print(sleep_entry["logId"])
```

Endpoints that support pagination:

- `get_sleep_log_list()`
- `get_activity_log_list()`
- `get_ecg_log_list()`
- `get_irn_alerts_list()`

For more details, see [PAGINATION.md](docs/PAGINATION.md).

## Rate Limiting

The client includes automatic retry handling for rate-limited requests. When a
rate limit is encountered, the client will:

1. Log the rate limit event
2. Wait using an exponential backoff strategy
3. Automatically retry the request

You can configure rate limiting behavior:

```python
client = FitbitClient(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="https://localhost:8080",
    max_retries=5,                # Maximum number of retry attempts (default: 3)
    retry_after_seconds=30,       # Base wait time in seconds (default: 60)
    retry_backoff_factor=2.0      # Multiplier for successive waits (default: 1.5)
)
```

For more details, see [RATE_LIMITING.md](docs/RATE_LIMITING.md).

## Additional Documentation

### For API Library Users

- [LOGGING.md](docs/LOGGING.md): Understanding the dual-logger system
- [TYPES.md](docs/TYPES.md): JSON type system and method return types
- [NAMING.md](docs/NAMING.md): API method naming conventions
- [VALIDATIONS.md](docs/VALIDATIONS.md): Input parameter validation
- [ERROR_HANDLING.md](docs/ERROR_HANDLING.md): Exception hierarchy and handling
- [PAGINATION.md](docs/PAGINATION.md): Working with paginated endpoints
- [RATE_LIMITING.md](docs/RATE_LIMITING.md): Rate limit handling and
  configuration

It's also worth reviewing
[Fitbit's Best Practices](https://dev.fitbit.com/build/reference/web-api/developer-guide/best-practices/)
for API usage.

### Project Best Practices

- [DEVELOPMENT.md](docs/DEVELOPMENT.md): Development environment and guidelines
- [LINTING.md](docs/LINTING.md): Code style and linting configuration

## Important Note - Subscription Support

This client does not currently support the
[creation](https://dev.fitbit.com/build/reference/web-api/subscription/create-subscription/)
and
[deletion](https://dev.fitbit.com/build/reference/web-api/subscription/delete-subscription/)
of
[webhook subscriptions](https://dev.fitbit.com/build/reference/web-api/developer-guide/using-subscriptions/).
The methods are implemented in comments and should work, but I have not had a
chance to verify them since this requires a publicly accessible server to
receive webhook notifications.

If you're using this library with subscriptions and would like to help test and
implement this functionality, please open an issue or pull request!

## License

Copyright (C) 2025 Jon Stroop

This program is licensed under the GNU Affero General Public License Version 3.0
(AGPL-3.0). See the [LICENSE](LICENSE) file for details.

## Disclaimer

Fitbit™ is a trademark of Google LLC. This project is designed for use with the
Fitbit API but is not endorsed, certified, or otherwise approved by Google or
Fitbit.
