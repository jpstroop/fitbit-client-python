# Conventions, Patterns, and Development Guide

## Set up Development Environment

### Prerequisites

- Python 3.13+
- PDM
- Git
- ASDF (recommended)

### Download and Install the Source Code

1. Clone the repository:

```bash
git clone https://github.com/jpstroop/fitbit-client-python.git
cd fitbit-client-python
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
pdm install -G:all
```

## Project Structure

```
fitbit-client/
├── fitbit_client/
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── callback_handler.py
│   │   ├── callback_server.py
│   │   └── oauth.py
│   ├── client.py
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── [resource modules]
│   │   ├── _base.py
│   │   ├── _pagination.py
│   │   └── _constants.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── curl_debug_mixin.py
│   │   ├── date_validation.py
│   │   ├── helpers.py
│   │   ├── pagination_validation.py
│   │   └── types.py
│   └── exceptions.py
└── tests/
    │   ├── fitbit_client/
    │   ├── auth/
    │   ├── resources/
    │   └── utils/
    └── [project files]
```

## Development Tools and Standards

### Code Formatting and Style

- Black for code formatting (100 character line length)
- isort for import sorting
- Type hints required for all code (enforced by `mypy`)
- Docstrings required for all public methods (enforced by `test_docscrings.py`)

### Import Style

Prefer importing specific names rather than entire modules, one import per line.
Examples:

```
# Good
from os.path import join
from os.path import exists
from typing import Dict
from typing import List
from typing import Optional
from datetime import datetime

# Bad
from os.path import exists, join
from typing import Optional, Dict, List
import os
import typing
import datetime
```

The one exception to this rule is when an entire module needs to be mocked for
testing, in which case, at least for the `json` package from the standard
library, the entire package has to be imported. So `import json` is ok when that
circumstance arises.

### Run all formatters:

```bash
pdm run format
```

### Resource Implementation Guidelines

Follow your nose from `client.py` and the structure should be very clear.

#### Method Structure

- Include comprehensive docstrings with Args sections
- Keep parameter naming consistent across methods (see [Naming](docs/NAMING.md))
- Return `JSONDict` for `JSONList` for most methods (`get_activity_tcx` returns
  XML as a string)
- Return `None` for delete operations

### Error Handling

The codebase implements a comprehensive error handling system. See
[ERROR_HANDLING](docs/ERROR_HANDLING.md) and
[`exceptions.py`](fitbit_client/exceptions.py).

### Enum Usage

- Only use enums for validating request parameters, not responses
- Place all enums in [`constants.py`](fitbit_client/resources/_constants.py)
- Only import enums that are actively used in the class

## Logging System

The project implements two different logs in through the
[`BaseResource`](fitbit_client/resources/_base.py) class: application logging
for API interactions and data logging for tracking important response fields.
See [LOGGING](docs/LOGGING.md) for details.

## API Design

### Resource-Based API

The primary API structure is resource-based, organizing related endpoints into
dedicated resource classes based on the structure and organzation of the
[Fibit Web API](https://dev.fitbit.com/build/reference/web-api/) itself, e.g.

- `client.user` - User profile and badges endpoints
- `client.activity` - Activity tracking, goals, and summaries
- `client.sleep` - Sleep logs and goals
- etc.

### Method Aliases

All resource methods are also available directly from the client instance
through aliases. This means developers can choose between two equivalent
approaches:

```python
# Standard resource-based access
client.user.get_profile()
client.activity.get_daily_activity_summary(date="2025-03-06")

# Direct access via method aliases
client.get_profile()
client.get_daily_activity_summary(date="2025-03-06")
```

Method aliases were implemented because yyping
`client.resource_name.method_name(...)` with many parameters can be tedious,
especially when used frequently. All method aliases are set up in the
`_set_up_method_aliases()` method in the
[`FitbitClient`](fitbit_client/client.py) class, which is called during
initialization. Each alias is a direct reference to the corresponding resource
method, ensuring consistent behavior regardless of how the method is accessed.

## Testing

The project uses pytest for testing and follows a consistent testing approach
across all components. 100% coverage is expected.

### Test Organization

The test directory mirrors the main package structure within the `test`
directory. For the most part, the naming is 1:1 (`test_blah.py`) or otherwise
obvious--many tests modules were getting quite long and broken out either into
directories or with names that make it obvious as to hwat they are testing.

All resource mocks are in the root [conftest.py](tests/conftest.py).

### Response Mocking

# \<<\<<\<<< Updated upstream The test suite uses the `mock_response_factory` fixture from `tests/conftest.py` to create consistent, configurable mock responses. This is the required pattern for all tests that need to mock HTTP responses.

The test suite uses the `mock_response_factory` fixture from `tests/conftest.py`
to create consistent, configurable mock responses. This is the required pattern
for all tests that need to mock HTTP responses.

> > > > > > > Stashed changes

#### Standard Mock Response Pattern

```python
def test_some_endpoint(resource, mock_oauth_session, mock_response_factory):
    """Test description."""
    # Define expected data first
    expected_data = {"data": "test"}
    
    # Create mock response using the factory
    mock_response = mock_response_factory(200, expected_data)
    
    # Assign to oauth.request.return_value
    resource.oauth.request.return_value = mock_response
    
    # Call the method under test
    result = resource.some_method()
    
    # Assert against expected_data, not mock_response.json.return_value
    assert result == expected_data
```

#### Response Factory Examples

```python
# Success response with data
mock_response = mock_response_factory(200, {"data": "test"})

# Response with custom headers
mock_response = mock_response_factory(
    status_code=200,
    json_data={"data": "test"},
    headers={"custom-header": "value"}
)

# Delete/no content response (204)
mock_response = mock_response_factory(204)

# Error response
mock_response = mock_response_factory(
    400, 
    {"errors": [{"errorType": "validation", "message": "Error message"}]}
)

# Non-JSON response (XML)
mock_response = mock_response_factory(
    200, 
    headers={"content-type": "application/vnd.garmin.tcx+xml"},
    content_type="application/vnd.garmin.tcx+xml"
)
mock_response.text = "<xml>content</xml>"
```

#### Parameter Validation Pattern

# \<<\<<\<<< Updated upstream For tests that only need to verify parameter validation or endpoint construction (not response handling), it's acceptable to use the following alternative pattern:

For tests that only need to verify parameter validation or endpoint construction
(not response handling), it's acceptable to use the following alternative
pattern:

> > > > > > > Stashed changes

```python
def test_validation(resource):
    """Test parameter validation."""
    resource._make_request = Mock()
    resource.some_method(param="value")
    resource._make_request.assert_called_once_with(
        "endpoint/path", params={"param": "value"}, user_id="-", debug=False
    )
```

# This approach provides a clean, standardized way to create mock responses with \<<\<<\<<< Updated upstream the desired status code, data, and headers. All test files must use one of these patterns.

the desired status code, data, and headers. All test files must use one of these
patterns.

> > > > > > > Stashed changes

## OAuth Callback Implementation

The OAuth callback mechanism is implemented using two main classes:
`CallbackServer` and `CallbackHandler`.

### Implementation Flow

1. `CallbackServer` starts an HTTPS server on localhost with a dynamically
   generated SSL certificate
2. When the OAuth provider redirects to our callback URL, `CallbackHandler`
   receives the GET request
3. The handler stores the full callback URL path (including query parameters) on
   the server instance using `setattr(self.server, "last_callback", self.path)`
4. `CallbackServer.wait_for_callback()` polls for this stored path using
   `getattr()` until either:
   - The callback data is found (returns the URL path)
   - The timeout is reached (returns None)
5. When complete, `stop()` cleans up by:
   - Shutting down the HTTP server
   - Removing temporary certificate files
   - Clearing internal state

## Git Workflow

1. Create a new branch for your feature/fix
2. Make your changes, following the style guidelines (see also:
   [LINTING](docs/LINTING.md)) and [Git Hooks](#git-hooks)
3. Run formatting checks (`pdm run format`) and tests (`pdm run pytest`)
4. Submit a pull request with a clear description of changes
   - Keep messages concise and focused on what was changed
   - Use present tense

### Git Hooks

The project includes pre-commit hooks to ensure code quality. To set up the
hooks:

```bash
# From the repository root
./lint/set-up-hooks.sh
```

This will set up a pre-commit hook that automatically runs:

1. `pdm run format` - Runs black, isort, and adds file headers
2. `pdm run mypy` - Runs type checking
3. `pdm run pytest` - Runs all tests

If any of these checks fail, the commit will be blocked. Any formatting changes
made by the hook will be automatically added to the commit.

To bypass the hooks for a specific commit (not recommended for normal usage):

```bash
git commit --no-verify -m "Your commit message"
```

## Release Process

_This section will be documented as we near our first release._
