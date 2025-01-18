# Fitbit™ API Client

A fully-typed Python client for interacting with the Fitbit API, featuring OAuth2 PKCE authentication and resource-based API interactions.

## Installation

This package requires Python 3.10 or later.

```bash
pdm add fitbit-client
```

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

# Will prompt you to copy/paste the callback URL
client.authenticate()
```

## Setting Up Your Fitbit App

1. Go to dev.fitbit.com and create a new application
2. Set OAuth 2.0 Application Type to "Personal"
3. Set Callback URL to:
   - For automatic method: "https://localhost:8080"
   - For manual method: Your preferred redirect URI
4. Copy your Client ID and Client Secret

## Documentation

For detailed usage examples and API documentation, visit our [documentation site](https://fitbit-client.readthedocs.io/).

For development guidelines, see [DEVELOPMENT.md](DEVELOPMENT.md).

## License

Copyright (C) 2024 Jon Stroop

This program is licensed under the GNU Affero General Public License Version 3.0 (AGPL-3.0).
See the [LICENSE](LICENSE) file for details.

## Disclaimer

Fitbit™ is a trademark of Google LLC. This project is designed for use with the Fitbit API but is not endorsed, certified, or otherwise approved by Google or Fitbit.