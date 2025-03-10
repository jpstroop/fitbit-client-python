# Code Style and Linting

Linting and formatting are handled by [Black](https://github.com/psf/black),
[isort](https://github.com/pycqa/isort/),
[mdformat](https://github.com/executablebooks/mdformat),
[autoflake](https://github.com/PyCQA/autoflake) and a
[small script that adds a path comment](../lint/add_file_headers.py).

## Running the Linters

Run all formatters using:

```bash
pdm run format
```

This will:

- Format Python code with Black
- Sort imports with isort
- Format Markdown files with mdformat
- Remove unused imports with autoflake
- Add file path headers to Python files

## Code Organization

Every Python file follows a precise organizational structure with three distinct
import sections:

1. **Standard library imports** - marked with `# Standard library imports`
2. **Third-party imports** - marked with `# Third party imports`
3. **Project-specific imports** - marked with `# Local imports`

Each section should be alphabetically ordered and separated by exactly one blank
line.

### Example

```python
"""Module docstring explaining the purpose of this file."""

# Standard library imports
from datetime import datetime
from inspect import currentframe
from json import JSONDecodeError
from json import dumps
from typing import Any
from typing import Dict

# Third party imports
from requests import Response
from requests_oauthlib import OAuth2Session

# Local imports
from fitbit_client.exceptions import FitbitAPIException
from fitbit_client.resources._base import BaseResource
```

## Documentation Requirements

The test suite verifies that all public methods have comprehensive docstrings
that follow the Google style format with specific sections:

- API Reference
- Args
- Returns
- Raises
- Note (if applicable)

Our linting tools ensure consistent style throughout the codebase.
