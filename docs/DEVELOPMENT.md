# Conventions, Patterns, and Development Guide

## Set up Development Environment

### Prerequisites

- Python 3.13+
- PDM
- Git

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
│   │   ├── base.py
│   │   └── constants.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── curl_debug_mixin.py
│   │   ├── date_validation.py
│   │   ├── helpers.py
│   │   ├── pagination_validation.py
│   │   └── types.py
│   └── exceptions.py
├── tests/
│   ├── auth/
│   ├── resources/
│   └── utils/
└── [project files]
```

## Goals, Notes, and TODOs

For now these are just in [TODO.md](TODO.md); bigger work will eventually move
to Github tickets.

## Development Tools and Standards

### Code Formatting and Style

- Black for code formatting (100 character line length)
- isort for import sorting
- Type hints required for all code
- Docstrings required for all public methods

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

The one exception to this rule is when an entire module needs to be `mock`ed for
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
- Keep parameter naming consistent across methods
- Use "-" as default for user_id parameters
- Return Dict[str, Any] for most methods that return data
- Return None for delete operations

### Error Handling

The codebase implements a comprehensive error handling system through
[`exceptions.py`](fitbit_client/exceptions.py):

1. A base FitbitAPIException that captures:

   - HTTP status code
   - Error type
   - Error message
   - Field name (when applicable)

2. Specialized exceptions for different error scenarios:

   - InvalidRequestException for malformed requests
   - ValidationException for parameter validation failures
   - AuthorizationException for authentication issues
   - RateLimitExceededException for API throttling
   - SystemException for server-side errors

3. Mapping from HTTP status codes and API error types to appropriate exception
   classes

### Enum Usage

- Only use enums for validating request parameters, not responses
- Place all enums in constants.py
- Only import enums that are actively used in the class

## Logging System

The project implements two different logs in through the
[`BaseResource`](fitbit_client/resources/base.py) class: application logging for
API interactions and data logging for tracking important response fields. See
[LOGGING](docs/LOGGING.md) for details.

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

Method aliases were implemented for several important reasons:

1. **Reduced Verbosity**: Typing `client.resource_name.method_name(...)` with
   many parameters can be tedious, especially when used frequently.

2. **Flatter API Surface**: Many modern APIs prefer a flatter design that avoids
   deep nesting, making the API more straightforward to use.

3. **Method Name Uniqueness**: All resource methods in the Fitbit API have
   unique names (e.g., there's only one `get_profile()` method), making it safe
   to expose these methods directly on the client.

4. **Preserve Both Options**: By maintaining both the resource-based access and
   direct aliases, developers can choose the approach that best fits their needs
   \- organization or conciseness.

All method aliases are set up in the `_set_up_method_aliases()` method in the
[`FitbitClient`](fitbit_client/client.py) class, which is called during
initialization. Each alias is a direct reference to the corresponding resource
method, ensuring consistent behavior regardless of how the method is accessed.

## Testing

The project uses pytest for testing and follows a consistent testing approach
across all components.

### Test Organization

The test directory mirrors the main package structure (except that the root is
named "test" rather than "fitbit_client"), with corresponding test modules for
each component:

- auth/: Tests for authentication and OAuth functionality
- client/: Tests for the main client implementation
- resources/: Tests for individual API resource implementations

### Standard Test Fixtures

The test suite provides several standard fixtures for use across test modules:

```python
@fixture
def mock_oauth_session():
    """Provides a mock OAuth session for testing resources"""
    return Mock()

@fixture
def mock_logger():
    """Provides a mock logger for testing logging behavior"""
    return Mock()

@fixture
def base_resource(mock_oauth_session, mock_logger):
    """Creates a resource instance with mocked dependencies"""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return BaseResource(mock_oauth_session, "en_US", "en_US")
```

### Error Handling Tests

Tests verify proper error handling across the codebase. Common patterns include:

```python
def test_http_error_handling(resource):
    """Tests that HTTP errors are properly converted to exceptions"""
    with raises(InvalidRequestException) as exc_info:
        # Test code that should raise the exception
        pass
    assert exc_info.value.status_code == 400
    assert exc_info.value.error_type == "validation"
```

### Response Mocking

The test suite uses consistent patterns for mocking API responses:

```python
mock_response = Mock()
mock_response.json.return_value = {"data": "test"}
mock_response.headers = {"content-type": "application/json"}
mock_response.status_code = 200
```

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

This section will be documented as we near our first release.

## Pagination Implementation

The pagination implementation uses the following approach:

### Pagination Iterator

- Uses the `PaginatedIterator` class that implements the Python `Iterator`
  protocol
- Automatically handles fetching the next page when needed using the `next` URL
  from pagination metadata
- Properly handles edge cases like invalid responses, missing pagination data,
  and API errors

### Type Safety

- Uses `TYPE_CHECKING` from the typing module to avoid circular imports at
  runtime
- Maintains complete type safety and mypy compatibility
- All pagination-related code has 100% test coverage

### Resource Integration

Each endpoint that supports pagination has an `as_iterator` parameter that, when
set to `True`, returns a `PaginatedIterator` instead of the raw API response.
This makes it easy to iterate through all pages of results without manually
handling pagination.

## Intraday Data Support

This client implements intraday data endpoints (detailed heart rate, steps, etc)
through the `IntradayResource` class. These endpoints have some special
requirements if you're using them for anyone other that yourself. See the
[Intraday API documentation](https://dev.fitbit.com/build/reference/web-api/intraday/)
for more details.
