# Python API Client for Fitbit™

# Fitbit Client

[![CI](https://github.com/jpstroop/fitbit-client-python/actions/workflows/ci.yml/badge.svg)](https://github.com/jpstroop/fitbit-client-python/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/jpstroop/fitbit-client-python/graph/badge.svg?token=DM0JD8VKZ4)](https://codecov.io/gh/jpstroop/fitbit-client-python)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

A fully-typed Python client for interacting with the Fitbit API, featuring
OAuth2 PKCE authentication and resource-based API interactions.

**THIS IS WORK IN PROGRESS** most methods have been tested, but there is no test
coverage yet, and more work [TODO](TODO.md). YMMV.

## Installation

This package requires Python 3.13 or later.

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
    profile = client.user.get_profile()
    print(dumps(profile, indent=2))
    
except Exception as e:
    print(f"Error: {str(e)}")
```

The response will always be the body of the API response, and is almost always a
`Dict`, `List` or `None`. `nutrition.get_activity_tcx` is the exception. It
returns XML (as a `str`).

## Authentication Methods

### 1. Automatic (Recommended)

Uses a local callback server to automatically handle the OAuth2 flow:

```python
client = FitbitClient(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="https://localhost:8080",
    use_callback_server=True  # default is True
)

# Will open browser and handle callback automatically
client.authenticate()
```

### 2. Manual URL Copy/Paste

If you prefer not to use a local server:

```python
client = FitbitClient(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="YOUR_REGISTERED_REDIRECT_URI",
    token_cache_path="/tmp/fb_tokens.json",
    use_callback_server=True
)

# Will open a browser and start a server to complete the flow (default), or 
# prompt you on the command line to copy/paste the callback URL from the 
# browser (see `use_callback_server`)
client.authenticate()
```

## Setting Up Your Fitbit App

1. Go to dev.fitbit.com and create a new application
2. Set OAuth 2.0 Application Type to "Personal"
3. Set Callback URL to:
   - For automatic method: "https://localhost:8080"
   - For manual method: Your preferred redirect URI
4. Copy your Client ID and Client Secret

Additional documentation:

- To understand the logging implemementation, see [LOGGING](docs/LOGGING.md)
- To understand validations and the exception hierarchy, see
  [VALIDATIONS_AND_EXCEPTIONS](docs/VALIDATIONS_AND_EXCEPTIONS.md)
- For some general development guidelines, see
  [DEVELOPMENT](docs/DEVELOPMENT.md).
- For style guidelines (mostly enforced through varius linters and formatters)
  see [STYLE](docs/STYLE.md).

## Important Note - Subscription Support

This client does not currently support the
[creation](https://dev.fitbit.com/build/reference/web-api/subscription/create-subscription/)
and
[deletion](https://dev.fitbit.com/build/reference/web-api/subscription/delete-subscription/)
of
[webhook subscrptions](https://dev.fitbit.com/build/reference/web-api/developer-guide/using-subscriptions/).
The methods are implemented in comments and _should_ work, but I have not had a
chance to verify a user confirm this.

## License

Copyright (C) 2025 Jon Stroop

This program is licensed under the GNU Affero General Public License Version 3.0
(AGPL-3.0). See the [LICENSE](LICENSE) file for details.

## Disclaimer

Fitbit™ is a trademark of Google LLC. This project is designed for use with the
Fitbit API but is not endorsed, certified, or otherwise approved by Google or
Fitbit.
