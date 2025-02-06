# tests/utils/test_date_validation.py

# Standard library imports
from typing import Any
from typing import Dict
from typing import Optional

# Third party imports
import pytest

# Local imports
from fitbit_client.exceptions import InvalidDateException
from fitbit_client.exceptions import InvalidDateRangeException
from fitbit_client.utils.date_validation import validate_date_format
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.date_validation import validate_date_range
from fitbit_client.utils.date_validation import validate_date_range_params


class TestDateValidation:
    def test_validate_date_format_valid(self):
        """Test validate_date_format with valid inputs"""
        # These should not raise exceptions
        validate_date_format("today")
        validate_date_format("2024-02-13")
        validate_date_format("2024-12-31")
        validate_date_format("2024-01-01")

    def test_validate_date_format_invalid(self):
        """Test validate_date_format with invalid inputs"""
        invalid_dates = [
            "2024/02/13",
            "13-02-2024",
            "2024-13-01",
            "2024-02-31",
            "24-02-13",
            "2024-2-13",
            "2024-02-1",
            "",
            "invalid",
            "yesterday",
            "2024-02-13T00:00:00",
            "2024-02-13 00:00:00",
        ]  # wrong separators  # wrong order  # invalid month  # invalid day for February  # 2-digit year  # missing leading zeros  # missing leading zeros  # empty string  # nonsense string  # only "today" is allowed  # with time  # with time

        for invalid_date in invalid_dates:
            with pytest.raises(InvalidDateException) as exc:
                validate_date_format(invalid_date)
            assert exc.value.status_code == 400
            assert exc.value.error_type == "validation"
            assert exc.value.date_str == invalid_date
            assert f"Invalid date format. Expected YYYY-MM-DD, got: {invalid_date}" in str(
                exc.value
            )

    def test_validate_date_range_order(self):
        """Test validate_date_range date ordering"""
        # Valid date ranges
        validate_date_range("2024-02-01", "2024-02-13")
        validate_date_range("2024-02-13", "2024-02-13")  # same day

        # Invalid order should raise
        with pytest.raises(InvalidDateRangeException) as exc:
            validate_date_range("2024-02-13", "2024-02-01")
        assert f"Start date 2024-02-13 is after end date 2024-02-01" in str(exc.value)
        assert exc.value.start_date == "2024-02-13"
        assert exc.value.end_date == "2024-02-01"

    def test_validate_date_range_max_days(self):
        """Test validate_date_range max_days constraint"""
        # Should pass - exactly 30 days
        validate_date_range("2024-02-01", "2024-03-02", max_days=30)

        # Should raise - 31 days
        with pytest.raises(InvalidDateRangeException) as exc:
            validate_date_range("2024-02-01", "2024-03-03", max_days=30)
        assert exc.value.max_days == 30
        assert "Date range 2024-02-01 to 2024-03-03 exceeds maximum allowed 30 days" in str(
            exc.value
        )

    def test_validate_date_range_with_resource(self):
        """Test validate_date_range with resource name"""
        with pytest.raises(InvalidDateRangeException) as exc:
            validate_date_range(
                "2024-02-01", "2024-03-03", max_days=30, resource_name="test resource"
            )
        assert (
            "Date range 2024-02-01 to 2024-03-03 exceeds maximum allowed 30 days for test resource"
            in str(exc.value)
        )
        assert exc.value.resource_name == "test resource"

    def test_validate_date_param_decorator(self):
        """Test the validate_date_param decorator"""

        @validate_date_param("date")
        def dummy_func(date: str) -> str:
            return date

        assert dummy_func("today") == "today"
        assert dummy_func("2024-02-13") == "2024-02-13"

        with pytest.raises(InvalidDateException):
            dummy_func("invalid")

    def test_validate_date_range_params_decorator(self):
        """Test the validate_date_range_params decorator"""

        @validate_date_range_params(max_days=30)
        def dummy_func(start_date: str, end_date: str) -> Dict[str, Any]:
            return {"start": start_date, "end": end_date}

        result = dummy_func("2024-02-01", "2024-02-13")
        assert result == {"start": "2024-02-01", "end": "2024-02-13"}

        with pytest.raises(InvalidDateRangeException) as exc:
            dummy_func("2024-02-13", "2024-02-01")  # wrong order
        assert f"Start date 2024-02-13 is after end date 2024-02-01" in str(exc.value)

        with pytest.raises(InvalidDateRangeException) as exc:
            dummy_func("2024-02-01", "2024-03-03")  # too many days
        assert "Date range 2024-02-01 to 2024-03-03 exceeds maximum allowed 30 days" in str(
            exc.value
        )

    def test_validate_date_param_decorator_with_optional(self):
        """Test the validate_date_param decorator with optional parameter"""

        @validate_date_param("date")
        def dummy_func(date: Optional[str] = None) -> Optional[str]:
            return date

        # Should work with no parameter
        assert dummy_func() is None

        # Should work with None
        assert dummy_func(None) is None

        # Should work with valid date
        assert dummy_func("2024-02-13") == "2024-02-13"

        # Should raise with invalid date
        with pytest.raises(InvalidDateException):
            dummy_func("invalid")

    def test_validate_date_range_params_decorator_with_optional(self):
        """Test the validate_date_range_params decorator with optional parameters"""

        @validate_date_range_params(max_days=30)
        def dummy_func(
            start_date: Optional[str] = None, end_date: Optional[str] = None
        ) -> Dict[str, Any]:
            return {"start": start_date, "end": end_date}

        # Should work with no parameters
        assert dummy_func() == {"start": None, "end": None}

        # Should work with None values
        assert dummy_func(None, None) == {"start": None, "end": None}

        # Should work with one None value
        assert dummy_func("2024-02-13", None) == {"start": "2024-02-13", "end": None}
        assert dummy_func(None, "2024-02-13") == {"start": None, "end": "2024-02-13"}

        # Should work with both dates
        result = dummy_func("2024-02-01", "2024-02-13")
        assert result == {"start": "2024-02-01", "end": "2024-02-13"}
