# tests/utils/test_pagination_validation.py


# Third party imports
from pytest import raises

# Local imports
from fitbit_client.exceptions import PaginationException
from fitbit_client.resources.constants import SortDirection
from fitbit_client.utils.pagination_validation import validate_pagination_params


class TestPaginationValidation:
    def test_validate_pagination_params_success(self):
        """Test that valid parameters pass validation"""

        @validate_pagination_params()
        def dummy_func(
            before_date: str = None,
            after_date: str = None,
            sort: SortDirection = SortDirection.DESCENDING,
            limit: int = 100,
            offset: int = 0,
        ):
            return {"before": before_date, "after": after_date, "sort": sort, "limit": limit}

        # Test with before_date and DESCENDING
        result = dummy_func(before_date="2024-02-13", sort=SortDirection.DESCENDING)
        assert result["before"] == "2024-02-13"
        assert result["sort"] == SortDirection.DESCENDING

        # Test with after_date and ASCENDING
        result = dummy_func(after_date="2024-02-13", sort=SortDirection.ASCENDING)
        assert result["after"] == "2024-02-13"
        assert result["sort"] == SortDirection.ASCENDING

    def test_validate_pagination_params_missing_dates(self):
        """Test that omitting both date parameters raises exception"""

        @validate_pagination_params()
        def dummy_func(
            before_date: str = None,
            after_date: str = None,
            sort: SortDirection = SortDirection.DESCENDING,
            limit: int = 100,
            offset: int = 0,
        ):
            return True

        with raises(PaginationException) as exc_info:
            dummy_func()
        assert "Either before_date or after_date must be specified" in str(exc_info.value)

    def test_validate_pagination_params_invalid_offset(self):
        """Test that non-zero offset raises exception"""

        @validate_pagination_params()
        def dummy_func(
            before_date: str = "2024-02-13",
            sort: SortDirection = SortDirection.DESCENDING,
            limit: int = 100,
            offset: int = 1,
        ):
            return True

        with raises(PaginationException) as exc_info:
            dummy_func()
        assert "Only offset=0 is supported" in str(exc_info.value)
        assert exc_info.value.field_name == "offset"

    def test_validate_pagination_params_invalid_limit(self):
        """Test that exceeding max limit raises exception"""

        @validate_pagination_params(max_limit=10)
        def dummy_func(
            before_date: str = "2024-02-13",
            sort: SortDirection = SortDirection.DESCENDING,
            limit: int = 11,
            offset: int = 0,
        ):
            return True

        with raises(PaginationException) as exc_info:
            dummy_func()
        assert "Maximum limit is 10" in str(exc_info.value)
        assert exc_info.value.field_name == "limit"

    def test_validate_pagination_params_sort_validation(self):
        """Test validation of sort direction matching date parameters"""

        @validate_pagination_params()
        def dummy_func(
            before_date: str = None,
            after_date: str = None,
            sort: SortDirection = SortDirection.ASCENDING,
            limit: int = 100,
            offset: int = 0,
        ):
            return True

        # Test invalid sort with before_date
        with raises(PaginationException) as exc_info:
            dummy_func(before_date="2024-02-13", sort=SortDirection.ASCENDING)
        assert "Must use sort=DESCENDING with before_date" in str(exc_info.value)
        assert exc_info.value.field_name == "sort"

        # Test invalid sort with after_date
        with raises(PaginationException) as exc_info:
            dummy_func(after_date="2024-02-13", sort=SortDirection.DESCENDING)
        assert "Must use sort=ASCENDING with after_date" in str(exc_info.value)
        assert exc_info.value.field_name == "sort"

    def test_validate_pagination_params_custom_field_names(self):
        """Test that custom field names are respected in error messages"""

        @validate_pagination_params(
            before_field="from_date",
            after_field="to_date",
            sort_field="direction",
            limit_field="count",
            offset_field="start",
        )
        def dummy_func(
            from_date: str = None,
            to_date: str = None,
            direction: SortDirection = SortDirection.DESCENDING,
            count: int = 100,
            start: int = 0,
        ):
            return True

        with raises(PaginationException) as exc_info:
            dummy_func(start=1)
        assert exc_info.value.field_name == "start"
        assert "Only offset=0 is supported" in str(exc_info.value)

        with raises(PaginationException) as exc_info:
            dummy_func(count=101)
        assert exc_info.value.field_name == "count"
        assert "Maximum limit is 100" in str(exc_info.value)

        with raises(PaginationException) as exc_info:
            dummy_func()
        assert "Either from_date or to_date must be specified" in str(exc_info.value)
