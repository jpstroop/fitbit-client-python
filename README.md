# Python API Client for Fitbit™

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![PDM](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

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

The response will always be a `Dict` with two keys: `headers` (the HTTP headers
returned by the API call), and `content`, which is the API response. This
approach allows us to almost completely encapsulate the HTTP(S) interactions
entirely (exceptions are the, erm, exception) and also makes strong typing more
predictable.

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
    use_callback_server=False
)

# Will prompt you on the command line to copy/paste the callback URL
client.authenticate()
```

## Setting Up Your Fitbit App

1. Go to dev.fitbit.com and create a new application
2. Set OAuth 2.0 Application Type to "Personal"
3. Set Callback URL to:
   - For automatic method: "https://localhost:8080"
   - For manual method: Your preferred redirect URI
4. Copy your Client ID and Client Secret

For development guidelines, see [DEVELOPMENT.md](DEVELOPMENT.md).

## Important Note - Intraday Data Support

- This client does not currently support intraday data endpoints (detailed heart
  rate, steps, etc). These endpoints require special access from Fitbit and are
  typically limited to research applications.
- For intraday data access requests, see
  [Fitbit's API documentation](https://dev.fitbit.com/build/reference/web-api/intraday/).
- See additional notes about this in [DEVELOPMENT.md](DEVELOPMENT.md)

## License

Copyright (C) 2025 Jon Stroop

This program is licensed under the GNU Affero General Public License Version 3.0
(AGPL-3.0). See the [LICENSE](LICENSE) file for details.

## Disclaimer

Fitbit™ is a trademark of Google LLC. This project is designed for use with the
Fitbit API but is not endorsed, certified, or otherwise approved by Google or
Fitbit.
