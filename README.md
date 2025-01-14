# Fitbit™ API Client

A Python client for interacting with the Fitbit API, featuring OAuth2 PKCE authentication and resource-based API interactions.

## Features

* OAuth2 PKCE authentication flow with automatic token refresh
* Token caching for persistent authentication
* Fully type-annotated
* Resource-based separation of concerns

## Installation

This package requires Python 3.13 or later.

```bash
pdm add fitbit-client
```

## Usage

```python
from fitbit_client import FitbitClient

# Initialize the client
client = FitbitClient(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="YOUR_REDIRECT_URI"
)

# Authenticate (will open browser for OAuth flow)
client.authenticate()

# Get user profile
profile = client.profile.get_profile()

# Log water intake
water_log = client.nutrition.log_water(
    amount=8,
    unit='cup'
)

# Get daily food log
food_log = client.nutrition.get_food_logs()
```

## Getting Started with Development

### Prerequisites

* Python 3.13+ (managed via asdf)
* PDM (managed via asdf)

### Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fitbit-client.git
cd fitbit-client
```

2. Install asdf plugins and required versions:
```bash
asdf plugin add python
asdf plugin add pdm
asdf install python 3.13.0
asdf install pdm latest
asdf local python 3.13.0
asdf local pdm latest
```

3. Install project dependencies:
```bash
pdm install -G dev
```

### Development Tools

This project uses several development tools, configured in `pyproject.toml`:

* Black - Code formatting
* isort - Import sorting

Run all formatters with:
```bash
pdm run fmt
```

### Project Structure

```
fitbit_client/
├── __init__.py
├── auth.py           # OAuth2 PKCE implementation
├── client.py         # Main client class
└── resources/        # API resource implementations
    ├── __init__.py
    ├── base.py
    ├── profile.py
    └── nutrition.py
    └── etc ... 
```

### Configuration Files

See `pyproject.toml`

## Credentials Setup

1. First, obtain your Fitbit API credentials:
   * Go to [dev.fitbit.com](https://dev.fitbit.com)
   * Log in and create a new application
   * Set OAuth 2.0 Application Type to "Personal"
   * Add your redirect URI (e.g., http://localhost:8080)
   * Save your Client ID and Client Secret

2. Create a `secrets.json` file in your project root (see [secrets.json.example](secrets.json.example):
```json
{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uri": "https://localhost:8080"
}
```

3. In your code, load the credentials:
```python
from json import load

with open("secrets.json") as f:
    secrets = load(f)
    
client = FitbitClient(**secrets)
client.authenticate()
```

See [main.py](main.py) for a basic example.

## License

Copyright (C) 2024 Jon Stroop

This program is licensed under the GNU Affero General Public License Version 3.0 (AGPL-3.0).
See the [LICENSE](LICENSE) file for details.

## Disclaimer

Fitbit™ is a trademark of Google LLC. This project is designed for use with the Fitbit API but is not endorsed, certified, or otherwise approved by Google or Fitbit.