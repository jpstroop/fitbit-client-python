# fitbit_client/utils/pagination_validation.py

# Standard library imports
from functools import wraps
from inspect import signature
from typing import Callable
from typing import Optional
from typing import ParamSpec
from typing import TypeVar
from typing import cast

# Local imports
from fitbit_client.exceptions import PaginationException
from fitbit_client.resources.constants import SortDirection

# Type variables for decorator typing
P = ParamSpec("P")
R = TypeVar("R")


def validate_pagination_params(
    before_field: str = "before_date",
    after_field: str = "after_date",
    sort_field: str = "sort",
    limit_field: str = "limit",
    offset_field: str = "offset",
    max_limit: int = 100,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator to validate pagination parameters commonly used in list endpoints.

    Validates:
    - Either before_date or after_date must be specified
    - Sort direction must match the date parameter used (ascending with after_date, descending with before_date)
    - Offset must be 0 for endpoints that don't support true pagination
    - Limit must not exceed the specified maximum

    Args:
        before_field: Name of the before date parameter (default: "before_date")
        after_field: Name of the after date parameter (default: "after_date")
        sort_field: Name of the sort direction parameter (default: "sort")
        limit_field: Name of the limit parameter (default: "limit")
        offset_field: Name of the offset parameter (default: "offset")
        max_limit: Maximum allowed value for limit parameter (default: 100)

    Returns:
        Decorated function that validates pagination parameters

    Example:
        ```python
        @validate_pagination_params(max_limit=10)
        def get_log_list(
            self,
            before_date: Optional[str] = None,
            after_date: Optional[str] = None,
            sort: SortDirection = SortDirection.DESCENDING,
            limit: int = 10,
            offset: int = 0,
        ):
            ...
        ```

    Raises:
        PaginatonError: If neither before_date nor after_date is specified
        PaginatonError: If offset is not 0
        PaginatonError: If limit exceeds 10
        PaginatonError: If sort is not 'asc' or 'desc'
        PaginatonError: If sort direction doesn't match date parameter
        InvalidDateException: If date format is invalid
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Bind arguments to get access to parameter values
            sig = signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Extract parameters
            before_date = bound_args.arguments.get(before_field)
            after_date = bound_args.arguments.get(after_field)
            sort = bound_args.arguments.get(sort_field)
            limit = bound_args.arguments.get(limit_field)
            offset = bound_args.arguments.get(offset_field)

            # Validate offset
            if offset != 0:
                raise PaginationException(
                    message="Only offset=0 is supported. Use pagination links in response for navigation.",
                    field_name=offset_field,
                )

            # Validate limit - add null check to fix mypy error
            if limit is not None and limit > max_limit:
                raise PaginationException(
                    message=f"Maximum limit is {max_limit}", field_name=limit_field
                )

            # Validate sort value
            if not isinstance(sort, SortDirection):
                raise PaginationException(
                    message="Sort must be a SortDirection enum value", field_name=sort_field
                )

            # Validate date parameters are present
            if not before_date and not after_date:
                raise PaginationException(
                    message=f"Either {before_field} or {after_field} must be specified"
                )

            # Validate sort direction matches date parameter
            if before_date and sort != SortDirection.DESCENDING:
                raise PaginationException(
                    message=f"Must use sort=DESCENDING with {before_field}", field_name=sort_field
                )
            if after_date and sort != SortDirection.ASCENDING:
                raise PaginationException(
                    message=f"Must use sort=ASCENDING with {after_field}", field_name=sort_field
                )

            return func(*args, **kwargs)

        return cast(Callable[P, R], wrapper)

    return decorator
