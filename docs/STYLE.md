# Code Style

Linting and formatting are handled by [Black](https://github.com/psf/black),
[isort](https://github.com/pycqa/isort/),
[mdformat](https://github.com/executablebooks/mdformat),
[autoflake](https://github.com/PyCQA/autoflake) and a
[small script that adds a path comment](/lint/add_file_headers.py). That said,
here are some general guidelines:

## Code Organization and Structure

Every Python file in the codebase must follow a precise organizational structure
that begins with the module-level docstring, followed by three distinct import
sections. These sections are separated by exactly one blank line between them
and are marked with specific comments.

The first section contains standard library imports with the comment "# Standard
library imports". These imports must be in alphabetical order. Related imports
from the same module, particularly typing imports, must be grouped together. For
example:

```python
# Standard library imports
from datetime import datetime
from inspect import currentframe
from json import JSONDecodeError
from json import dumps
from logging import getLogger
from typing import Any
from typing import Dict
from typing import Optional
from typing import Set
```

The second section contains third-party imports with the comment "# Third party
imports". These must also be alphabetically ordered:

```python
# Third party imports
from requests import Response
from requests_oauthlib import OAuth2Session
```

The third section contains project-specific imports with the comment "# Local
imports". These follow the same alphabetical ordering:

```python
# Local imports
from fitbit_client.exceptions import ERROR_TYPE_EXCEPTIONS
from fitbit_client.exceptions import FitbitAPIException
from fitbit_client.exceptions import STATUS_CODE_EXCEPTIONS
```

## Documentation Requirements

The codebase demonstrates strict documentation requirements at multiple levels.
Every module must begin with a comprehensive docstring that explains its
purpose, notes important details, and includes the API reference URL where
applicable. For example:

```python
"""
Handles Fitbit Active Zone Minutes (AZM) API endpoints for retrieving user's
heart-pumping activity data throughout the day.

Active Zone Minutes (AZM) measure the time spent in target heart rate zones.
Different zones contribute differently to the total AZM count:
- Fat Burn zone: 1 minute = 1 AZM
- Cardio zone: 1 minute = 2 AZM
- Peak zone: 1 minute = 2 AZM

API Reference: https://dev.fitbit.com/build/reference/web-api/active-zone-minutes-timeseries/
"""
```

Every method must have a complete docstring that follows the Google style format
with specific sections. These sections must appear in the following order: Args,
Returns, Raises, and Note. The docstring must describe all parameters, including
their optionality and default values. For example:

```python
def get_activity_tcx(
    self,
    log_id: int,
    include_partial_tcx: bool = False,
    user_id: str = "-",
    debug: bool = False,
) -> Dict[str, Any]:
    """
    Retrieves the TCX (Training Center XML) data for a specific activity log.

    TCX files contain GPS, heart rate, and lap data recorded during the logged exercise.

    Args:
        log_id: ID of the activity log to retrieve
        include_partial_tcx: Include TCX points when GPS data is not available.
            Defaults to False.
        user_id: Optional user ID. Defaults to "-" for current logged-in user.
        debug: If True, prints a curl command to stdout to help with debugging.
            Defaults to False.

    Returns:
        Response contains TCX data for the activity including GPS, heart rate,
        and lap information.

    Raises:
        InvalidDateException: If date format is invalid
        ValidationException: If log_id is invalid
        AuthorizationException: If missing required scopes

    Note:
        Requires both 'activity' and 'location' scopes to be authorized.
    """
```

## Testing Requirements

The test files demonstrate comprehensive requirements for test coverage and
organization. Each test file must be named test\_[resource_name].py and contain
a primary test class named Test[ResourceName]. For example, the tests for
activity.py must be in test_activity.py with a class named TestActivityResource.

Every test class must include fixtures that properly mock all dependencies. The
standard fixture pattern shown throughout the codebase is:

```python
@fixture
def resource_name(self, mock_oauth_session, mock_logger):
    """Create ResourceName instance with mocked dependencies"""
    with patch("fitbit_client.resources.base.getLogger", return_value=mock_logger):
        return ResourceName(mock_oauth_session, "en_US", "en_US")
```

Test coverage must be comprehensive, including both public and private methods.
Each test method must focus on a single behavior or condition and include
detailed verification of the expected outcome. The test name must clearly
describe what is being tested. For example:

```python
def test_get_activity_tcx_with_partial_data(self, activity_resource, mock_response):
    """Test retrieval of TCX data with partial data flag enabled"""
    mock_response.json.return_value = {"expected": "response"}
    activity_resource.oauth.request.return_value = mock_response

    result = activity_resource.get_activity_tcx(
        log_id=12345,
        include_partial_tcx=True
    )

    assert result == {"expected": "response"}
    activity_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/user/-/activities/12345.tcx",
        params={"includePartialTCX": True},
        data=None,
        json=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"}
    )
```

Error cases must be thoroughly tested using pytest's raises context manager,
verifying both the exception type and its attributes:

```python
def test_get_activity_tcx_invalid_log_id(self, activity_resource):
    """Test that invalid log ID raises ValidationException"""
    with raises(ValidationException) as exc_info:
        activity_resource.get_activity_tcx(log_id=-1)
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.error_type == "validation"
    assert exc_info.value.field_name == "log_id"
    assert "Invalid log ID" in str(exc_info.value)
```

## Exception Handling

The codebase defines a strict exception hierarchy based on FitbitAPIException.
All custom exceptions must inherit from this base class and include specific
attributes:

```python
class CustomException(FitbitAPIException):
    """Raised when [specific condition occurs]"""

    def __init__(
        self,
        message: str,
        status_code: int,
        error_type: str,
        field_name: Optional[str] = None
    ):
        super().__init__(
            message=message,
            status_code=status_code,
            error_type=error_type,
            field_name=field_name
        )
```

The codebase maintains two comprehensive exception mappings:

1. STATUS_CODE_EXCEPTIONS maps HTTP status codes to specific exception classes
2. ERROR_TYPE_EXCEPTIONS maps Fitbit API error types to exception classes

## Resource Implementation

All resource classes must inherit from BaseResource and follow consistent
patterns for method implementation. Every method that interacts with the API
must:

1. Use type hints for all parameters and return values
2. Provide a default of "-" for user_id parameter
3. Include a debug parameter defaulting to False
4. Use appropriate validation decorators for dates and ranges
5. Follow consistent naming conventions (get\_, create\_, delete\_)

Method implementation must handle API responses appropriately:

```python
def get_example_data(
    self,
    param: str,
    user_id: str = "-",
    debug: bool = False
) -> Dict[str, Any]:
    """Method docstring following standard format"""
    return self._make_request(
        f"endpoint/{param}.json",
        user_id=user_id,
        debug=debug
    )
```

## Date Handling

The codebase shows strict requirements for date handling through two key
decorators:

1. @validate_date_param() for single dates
2. @validate_date_range_params() for date ranges

These decorators enforce:

- YYYY-MM-DD format
- Acceptance of "today" as a valid value
- Proper ordering of date ranges
- Maximum range limits per endpoint

The implementation must use these decorators consistently for all date-related
parameters.
