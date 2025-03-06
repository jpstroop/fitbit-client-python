# Conventions, Patterns, and Development Guide

## Contents

- [Development Environment Setup](#development-environment-setup)
  - [Prerequisites](#prerequisites)
  - [Initial Setup](#initial-setup)
- [Project Structure](#project-structure)
- [Goals, Notes, and TODOs](#goals-notes-and-todos)
- [Development Tools and Standards](#development-tools-and-standards)
  - [Code Formatting and Style](#code-formatting-and-style)
  - [Import Style](#import-style)
  - [Resource Implementation Guidelines](#resource-implementation-guidelines)
  - [Error Handling](#error-handling)
  - [Enum Usage](#enum-usage)
- [Logging System](#logging-system)
  - [Application Logger](#application-logger)
  - [Data Logger](#data-logger)
- [API Design](#api-design)
  - [Resource-Based API](#resource-based-api)
  - [Method Aliases](#method-aliases)
- [Testing](#testing)
  - [Test Organization](#test-organization)
  - [Standard Test Fixtures](#standard-test-fixtures)
  - [Error Handling Tests](#error-handling-tests)
  - [Response Mocking](#response-mocking)
- [OAuth Callback Implementation](#oauth-callback-implementation)
  - [Implementation Flow](#implementation-flow)
  - [Security Notes](#security-notes)
- [Git Workflow](#git-workflow)
- [Release Process](#release-process)
- [Getting Help](#getting-help)
- [Scope and Limitations - Intraday Data Support](#scope-and-limitations---intraday-data-support)

## Development Environment Setup

### Prerequisites

- Python 3.12+
- PDM
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
asdf install python 3.12.0
asdf install pdm latest
asdf local python 3.12.0
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
│   ├── client/
│   │   ├── __init__.py
│   │   ├── fitbit_client.py
│   │   └── resource_methods_mixin.py
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── [resource files]
│   │   └── constants.py
│   └── exceptions.py
├── tests/
│   ├── auth/
│   ├── client/
│   └── resources/
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

The one excpetion to this rule is when an entire module needs to be `mock`ed for
testing, in which case, at least for the `json` package from the standare
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

The project implements dual logging through the BaseResource class: application
logging for API interactions and data logging for tracking important response
fields.

### Application Logger

Each resource class inherits logging functionality from BaseResource, which
initializes a logger with the resource's class name:

```python
self.logger = getLogger(f"fitbit_client.{self.__class__.__name__}")
```

The application logger handles:

- Success responses at INFO level
- Error responses at ERROR level
- Debug information about requests and responses
- Internal server logging

The BaseResource.\_log_response method standardizes log message formats:

- For errors: "[error_type] field_name: message" (if field name available)
- For success: "method succeeded for endpoint (status code)"

### Data Logger

The data logger specifically tracks important fields from API responses.
BaseResource defines these fields in IMPORTANT_RESPONSE_FIELDS:

```python
IMPORTANT_RESPONSE_FIELDS: Set[str] = {
    "access",   # PUBLIC/PRIVATE/SHARED
    "date",     # Dates
    "dateTime", # Timestamps
    "deviceId", # Device IDs
    "foodId",   # Food resource IDs
    "logId",    # Log entry IDs
    "name",     # Resource names
    "subscriptionId"  # Subscription IDs
}
```

The BaseResource.\_log_data method extracts and logs these fields when present
in API responses.

Data log entries contain:

- Timestamp (ISO format)
- Method name
- Important fields found in the response

This logging system provides both operational visibility through the application
logger and structured data capture through the data logger.

## API Design

The client implements a dual-level API design pattern that balances both
organization and ease-of-use.

### Resource-Based API

The primary API structure is resource-based, organizing related endpoints into
dedicated resource classes:

- `client.user` - User profile and badges endpoints
- `client.activity` - Activity tracking, goals, and summaries
- `client.sleep` - Sleep logs and goals
- etc.

This organization provides a clean separation of concerns and makes the code
more maintainable by grouping related functionality.

### Method Aliases

To improve developer experience, all resource methods are also available
directly from the client instance through aliases. This means developers can
choose between two equivalent approaches:

```python
# Standard resource-based access
client.user.get_profile()
client.activity.get_daily_activity_summary(date="2025-03-06")

# Direct access via method aliases
client.get_profile()
client.get_daily_activity_summary(date="2025-03-06")
```

#### Rationale for Method Aliases

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

All method aliases are set up in the `_setup_method_aliases()` method in the
`FitbitClient` class, which is called during initialization. Each alias is a
direct reference to the corresponding resource method, ensuring consistent
behavior regardless of how the method is accessed.

## Testing

The project uses pytest for testing and follows a consistent testing approach
across all components.

### Test Organization

The test directory mirrors the main package structure, with corresponding test
modules for each component:

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

### Security Notes

TODO

## Git Workflow

1. Create a new branch for your feature/fix
2. Make your changes, following the style guidelines
3. Run formatting checks (`pdm format`)
4. Submit a pull request with a clear description of changes

## Release Process

TODO

## Getting Help

- Check existing issues before creating new ones
- Use issue templates when reporting bugs
- Include Python version and environment details in bug reports

## Intraday Data Support

This client implements intraday data endpoints (detailed heart rate, steps, etc)
through the `IntradayResource` class. These endpoints:

- Require special access from Fitbit (typically limited to research
  applications)
- Have different rate limits than standard endpoints
- Need additional OAuth2 scopes (specifically the 'activity' and 'heartrate'
  scopes)
- Often require institutional review board (IRB) approval for research
  applications

To use intraday data:

1. Apply for intraday access through the
   [Fitbit developer portal](https://dev.fitbit.com/)
2. Ensure your application requests the appropriate scopes
3. Use the intraday methods with appropriate detail level parameters:
   ```python
   client.intraday.get_heartrate_intraday_by_date(
       date="today",
       detail_level="1min"  # or "1sec" depending on your access level
   )
   ```

See the
[Intraday API documentation](https://dev.fitbit.com/build/reference/web-api/intraday/)
for more details on available endpoints and access requirements.
