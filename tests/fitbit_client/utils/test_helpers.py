# tests/fitbit_client/utils/test_helpers.py

"""
Tests for utility functions in the fitbit_client.utils.helpers module.

This module verifies the functionality of helper functions used across
the Fitbit client including string transformations, JSON formatting,
and date range generation.
"""

# Standard library imports
from io import StringIO
import json
from typing import Iterator

# Local imports
from fitbit_client.utils.helpers import date_range
from fitbit_client.utils.helpers import print_json
from fitbit_client.utils.helpers import to_camel_case


def test_to_camel_case_default():
    """Test converting snake_case to camelCase with default settings."""
    # Test basic conversion
    assert to_camel_case("hello_world") == "helloWorld"

    # Test with multiple underscores
    assert to_camel_case("user_first_name") == "userFirstName"

    # Test with single word
    assert to_camel_case("hello") == "hello"

    # Test with empty string
    assert to_camel_case("") == ""


def test_to_camel_case_with_cap_first():
    """Test converting snake_case to CamelCase with cap_first=True."""
    # Test basic conversion
    assert to_camel_case("hello_world", cap_first=True) == "HelloWorld"

    # Test with multiple underscores
    assert to_camel_case("user_first_name", cap_first=True) == "UserFirstName"

    # Test with single word
    assert to_camel_case("hello", cap_first=True) == "Hello"

    # Test with empty string
    assert to_camel_case("", cap_first=True) == ""


def test_to_camel_case_with_uppercase():
    """Test converting snake_case with uppercase letters."""
    # Test with uppercase in input
    assert to_camel_case("HELLO_WORLD") == "helloWorld"
    assert to_camel_case("Hello_World") == "helloWorld"

    # Test with mixed case
    assert to_camel_case("API_response_code") == "apiResponseCode"


def test_print_json_basic():
    """Test JSON pretty printing with basic object."""
    # Create a StringIO object to capture the output
    test_output = StringIO()
    test_data = {"name": "John", "age": 30}

    # Call the function with our test data and output stream
    print_json(test_data, test_output)

    # Get the printed content and reset the cursor
    test_output.seek(0)
    printed_json = test_output.read().strip()

    # Parse the printed JSON to compare with original data
    parsed_json = json.loads(printed_json)
    assert parsed_json == test_data

    # Verify indentation and formatting
    assert "  " in printed_json  # Should have 2-space indentation


def test_print_json_complex():
    """Test JSON pretty printing with complex nested object."""
    test_output = StringIO()
    test_data = {
        "person": {
            "name": "John Doe",
            "age": 30,
            "address": {"street": "123 Main St", "city": "Anytown"},
            "hobbies": ["reading", "cycling", "coding"],
        }
    }

    print_json(test_data, test_output)

    test_output.seek(0)
    printed_json = test_output.read().strip()
    parsed_json = json.loads(printed_json)

    assert parsed_json == test_data
    assert "  " in printed_json


def test_print_json_unicode():
    """Test JSON pretty printing with Unicode characters."""
    test_output = StringIO()
    test_data = {"name": "Jöhn Dôë", "city": "Münich"}

    print_json(test_data, test_output)

    test_output.seek(0)
    printed_json = test_output.read().strip()
    parsed_json = json.loads(printed_json)

    assert parsed_json == test_data
    # Verify Unicode characters are preserved (not escaped)
    assert "Jöhn" in printed_json
    assert "\\u" not in printed_json  # No Unicode escaping


def test_print_json_functionality():
    """Test that print_json can format JSON correctly (without testing stdout)."""
    # Instead of testing stdout capture, we'll verify the function works
    # by examining what happens when we pass a StringIO object directly

    test_data = {"test": "value"}
    output_stream = StringIO()

    # Use our function with an explicit file object
    print_json(test_data, output_stream)

    # Reset the cursor position
    output_stream.seek(0)
    output = output_stream.getvalue().strip()

    # Verify output is valid JSON and matches expected data
    parsed_json = json.loads(output)
    assert parsed_json == test_data

    # Verify formatting features (indentation)
    assert "  " in output


def test_date_range_forward():
    """Test date_range with end_date after start_date."""
    start = "2023-01-01"
    end = "2023-01-05"

    result = list(date_range(start, end))

    expected = ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"]

    assert result == expected
    assert len(result) == 5


def test_date_range_backward():
    """Test date_range with end_date before start_date."""
    start = "2023-01-05"
    end = "2023-01-01"

    result = list(date_range(start, end))

    expected = ["2023-01-05", "2023-01-04", "2023-01-03", "2023-01-02", "2023-01-01"]

    assert result == expected
    assert len(result) == 5


def test_date_range_same_day():
    """Test date_range with start_date equal to end_date."""
    start = "2023-01-01"
    end = "2023-01-01"

    result = list(date_range(start, end))

    expected = ["2023-01-01"]

    assert result == expected
    assert len(result) == 1


def test_date_range_year_boundary():
    """Test date_range crossing year boundary."""
    start = "2022-12-30"
    end = "2023-01-02"

    result = list(date_range(start, end))

    expected = ["2022-12-30", "2022-12-31", "2023-01-01", "2023-01-02"]

    assert result == expected
    assert len(result) == 4


def test_date_range_month_boundary():
    """Test date_range crossing month boundary."""
    start = "2023-01-30"
    end = "2023-02-02"

    result = list(date_range(start, end))

    expected = ["2023-01-30", "2023-01-31", "2023-02-01", "2023-02-02"]

    assert result == expected
    assert len(result) == 4


def test_date_range_leap_year():
    """Test date_range with leap year February."""
    start = "2020-02-28"
    end = "2020-03-01"

    result = list(date_range(start, end))

    expected = ["2020-02-28", "2020-02-29", "2020-03-01"]

    assert result == expected
    assert len(result) == 3


def test_date_range_return_type():
    """Test that date_range returns an iterator."""
    start = "2023-01-01"
    end = "2023-01-03"

    result = date_range(start, end)

    assert isinstance(result, Iterator)
