# fitbit_client/utils/date_validation.py

# Standard library imports
from datetime import date
from datetime import datetime
from functools import wraps
from inspect import signature
from typing import Callable
from typing import Optional
from typing import TypeVar
from typing import cast

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException

# Type variable for the decorator
F = TypeVar("F", bound=Callable)


def validate_date_format(date_str: str, field_name: str = "date") -> None:
    """
    Validates that a date string is either 'today' or YYYY-MM-DD format.

    This function can be used in two ways:
    1. Directly, for one-off validations especially with optional parameters:
        ```python
        if date_param:
            validate_date_format(date_param, "date_param")
        ```
    2. Via the @validate_date_param decorator for required date parameters:
        ```python
        @validate_date_param()
        def my_method(self, date: str):
            ...
        ```

    Args:
        date_str: Date string to validate
        field_name: Name of field for error messages

    Raises:
        InvalidDateException: If date format is invalid
    """
    if date_str == "today":
        return

    # Quick format check before attempting to parse
    if not (
        len(date_str) == 10
        and date_str[4] == "-"
        and date_str[7] == "-"
        and all(c.isdigit() for c in (date_str[0:4] + date_str[5:7] + date_str[8:10]))
    ):
        raise InvalidDateException(date_str, field_name)

    try:
        # Now validate calendar date
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise InvalidDateException(date_str, field_name)


def validate_date_range(
    start_date: str,
    end_date: str,
    max_days: Optional[int] = None,
    resource_name: Optional[str] = None,
) -> None:
    """
    Validates a date range.

    This function can be used in two ways:
    1. Directly, for one-off validations especially with optional parameters:
        ```python
        if start_date and end_date:
            validate_date_range(start_date, end_date, max_days=30)
        ```
    2. Via the @validate_date_range_params decorator for required parameters:
        ```python
        @validate_date_range_params(max_days=30)
        def my_method(self, start_date: str, end_date: str):
            ...
        ```

    Args:
        start_date: Start date in YYYY-MM-DD format or 'today'
        end_date: End date in YYYY-MM-DD format or 'today'
        max_days: Optional maximum number of days between dates
        resource_name: Optional resource name for error messages

    Raises:
        InvalidDateException: If date format is invalid
        InvalidDateRangeException: If date range is invalid or exceeds max_days
    """
    # Validate individual date formats first
    validate_date_format(start_date, "start_date")
    validate_date_format(end_date, "end_date")

    # Convert to date objects for comparison
    start = (
        date.today() if start_date == "today" else datetime.strptime(start_date, "%Y-%m-%d").date()
    )
    end = date.today() if end_date == "today" else datetime.strptime(end_date, "%Y-%m-%d").date()

    # Check order
    if start > end:
        raise InvalidDateRangeException(
            start_date, end_date, f"Start date {start_date} is after end date {end_date}"
        )

    # Check max_days if specified and both dates are actual dates (not 'today')
    if max_days and start_date != "today" and end_date != "today":
        date_diff = (end - start).days
        if date_diff > max_days:
            resource_msg = f" for {resource_name}" if resource_name else ""
            raise InvalidDateRangeException(
                start_date,
                end_date,
                f"Date range {start_date} to {end_date} exceeds maximum allowed {max_days} days{resource_msg}",
                max_days,
                resource_name,
            )


def validate_date_param(field_name: str = "date") -> Callable[[F], F]:
    """
    Decorator to validate a single date parameter.

    Best used for methods with required date parameters. For optional date parameters,
    consider using validate_date_format() directly instead.

    Args:
        field_name: Name of field to validate in the decorated function

    Example:
        ```python
        @validate_date_param()
        def my_method(self, date: str):
            ...

        @validate_date_param(field_name="log_date")
        def another_method(self, log_date: str):
            ...
        ```
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            date = bound_args.arguments.get(field_name)

            if date:
                validate_date_format(date, field_name)
            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator


def validate_date_range_params(
    start_field: str = "start_date",
    end_field: str = "end_date",
    max_days: Optional[int] = None,
    resource_name: Optional[str] = None,
) -> Callable[[F], F]:
    """
    Decorator to validate date range parameters.

    Best used for methods with required date range parameters. For optional date parameters,
    consider using validate_date_range() directly instead.

    Args:
        start_field: Name of start date field in decorated function
        end_field: Name of end date field in decorated function
        max_days: Optional maximum allowed days between dates
        resource_name: Optional resource name for error messages

    Example:
        ```python
        @validate_date_range_params(max_days=30)
        def my_method(self, start_date: str, end_date: str):
            ...

        @validate_date_range_params(start_field="from_date", end_field="to_date", max_days=100)
        def another_method(self, from_date: str, to_date: str):
            ...
        ```
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            start_date = bound_args.arguments.get(start_field)
            end_date = bound_args.arguments.get(end_field)

            if start_date and end_date:
                validate_date_range(start_date, end_date, max_days, resource_name)
            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator
