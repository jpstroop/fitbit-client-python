# Development Guide

This guide covers everything you need to know to set up your development environment and contribute
to the Fitbit API Client project.

## Development Environment Setup

### Prerequisites

- Python 3.13+ (managed via asdf)
- PDM (managed via asdf)
- Git

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

## Project Structure

```
fitbit-client/
.
├── LICENSE
├── README.md
├── DEVELOPMENT.md
├── pdm.lock
├── pyproject.toml
├── client.py
├── auth
│   ├── callback_handler.py
│   ├── callback_server.py
│   └── oauth.py
└── resources
    ├── activezone.py
    ├── activity.py
    ├── activity_timeseries.py
    ├── base.py
    ├── body.py
    ├── body_timeseries.py
    ├── breathingrate.py
    ├── cardio_fitness.py
    ├── constants.py
    ├── device.py
    ├── ecg.py
    ├── friends.py
    ├── heartrate_timeseries.py
    ├── heartrate_variability.py
    ├── irregular_rhythm.py
    ├── nutrition.py
    ├── nutrition_timeseries.py
    ├── sleep.py
    ├── spo2.py
    ├── subscription.py
    ├── temperature.py
    └── user.py
```

## Goals, Notes, and TODOs

For now these are just in [TODO.md](TODO.md)

## Development Tools and Standards

### Code Formatting and Style

- Black for code formatting (100 character line length)
- isort for import sorting
- Type hints required for all code
- Docstrings required for all public methods

### Import Style

- Always import specific names rather than entire modules
- One import per line
- Examples:
  ```
  # Good
  from os.path import join
  from os.path import exists
  from typing import Dict
  from typing import List
  from typing import Optional
  from datetime import datetime

  # Avoid
  from os.path import exists, join
  from typing import Optional, Dict, List
  import os
  import typing
  import datetime
  ```

Run all formatters:

```bash
pdm run fmt
```

### Resource Implementation Guidelines

Follow your nose from `client.py` and the structure should be very clear.

#### Method Structure

- Include comprehensive docstrings with Args sections
- Keep parameter naming consistent across methods
- Use "-" as default for user_id parameters
- Return Dict[str, Any] for most methods that return data
- Return None for delete operations

#### Error Handling

- Include basic ValueError checks for required parameters
- Let the base class handle HTTP errors and authentication
- Document expected exceptions in docstrings

### Enum Usage

- Only use enums for validating request parameters, not responses
- Place all enums in constants.py
- Only import enums that are actively used in the class

## Testing

TODO/TBD

## Git Workflow

1. Create a new branch for your feature/fix
2. Make your changes, following the style guidelines
3. Run formatting checks (`pdm fmt`)
4. Submit a pull request with a clear description of changes

## Release Process

TODO

## Getting Help

- Check existing issues before creating new ones
- Use issue templates when reporting bugs
- Include Python version and environment details in bug reports

## Scope and Limitations - Intraday Data Support

This client explicitly does not implement intraday data endpoints (detailed heart rate, steps, etc).
These endpoints:

- Require special access from Fitbit (typically limited to research applications)
- Have different rate limits than standard endpoints
- Need additional OAuth2 scopes
- Often require institutional review board (IRB) approval

If you need intraday data access:

1. Apply through Fitbit's developer portal
2. Document your research use case
3. Obtain necessary approvals
4. Pull requests welcome!
