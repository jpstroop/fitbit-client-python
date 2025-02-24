# fitbit_client/utils/helpers.py

"""
Utility functions we often need when working with the Fitbit API.
"""

# Standard library imports
from datetime import date
from datetime import timedelta
from json import dumps
from sys import stdout
from typing import Iterator
from typing import TextIO

# Local imports
from fitbit_client.utils.types import JSONType


def to_camel_case(snake_str: str, cap_first: bool = False) -> str:
    """
    Convert a snake_case string to cameCase or CamelCase.

    Args:
        snake_str: a snake_case string
        cap_first: if True, returns CamelCase, otherwise camelCase (default is False)
    """
    if not snake_str:  # handle empty string case
        return ""

    camel_string = "".join(l.capitalize() for l in snake_str.lower().split("_"))
    if cap_first:
        return camel_string
    else:
        return snake_str[0].lower() + camel_string[1:]


def print_json(obj: JSONType, f: TextIO = stdout):
    """
    Pretty print JSON-serializable objects.

    Args:
        obj: Any JSON serializable object
        f: A file-like object to which the object should be serialized. Default: stdout
    """
    print(dumps(obj, ensure_ascii=False, indent=2), file=f, flush=True)


def date_range(start_date: str, end_date: str) -> Iterator[str]:
    """
    Generates dates between start_date and end_date inclusive, in ISO
    formatted (YYYY-MM-DD) strings. If the end date is before the start
    date, iterates in reverse. This is the date format the Fitbit API always
    wants, and it's useful in writing quick scripts for pulling down multiple
    days of data when another method is not supported.

    Args:
        start_date: Starting date in YYYY-MM-DD format
        end_date: Ending date in YYYY-MM-DD format

    Yields:
        str: Each date in the range in YYYY-MM-DD format
    """
    end = date.fromisoformat(end_date)
    start = date.fromisoformat(start_date)
    if end < start:
        while start >= end:
            yield start.isoformat()
            start -= timedelta(days=1)
    elif end > start:
        while start <= end:
            yield start.isoformat()
            start += timedelta(days=1)
    else:  # start == end
        yield start.isoformat()
