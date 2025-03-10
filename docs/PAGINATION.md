# Pagination

Some API endpoints return potentially large result sets and support pagination.
We provide an easy and pythonic way to work with these paginated endpoints as
iterators.

## Supported Endpoints

The following endpoints support pagination:

- `client.get_sleep_log_list()`
- `client.get_activity_log_list()`
- `client.get_ecg_log_list()`
- `client.get_irn_alerts_list()`

## Usage

### Standard Mode

By default, all endpoints return a single page of results with pagination
metadata:

```python
# Get a single (the first) page of sleep logs
sleep_data = client.get_sleep_log_list(
    before_date="2025-01-01",
    sort=SortDirection.DESCENDING,
    limit=10
)
```

### Iterator Mode

When you need to process multiple pages of data, use iterator mode:

```python
iterator = client.get_sleep_log_list(
    before_date="2025-01-01",
    sort=SortDirection.DESCENDING,
    limit=10,
    as_iterator=True # Creates an iterator for all pages
)

# Process all pages - the iterator fetches new pages as needed
for page in iterator:
    # Each page has the same structure as the standard response
    for sleep_entry in page["sleep"]:
        print(f"Sleep log ID: {sleep_entry['logId']}")
```

## Pagination Parameters

Different endpoints support different pagination parameters, but they generally
follow these patterns:

| Parameter     | Description                     | Constraints                                                 |
| ------------- | ------------------------------- | ----------------------------------------------------------- |
| `before_date` | Return entries before this date | Must use with `sort=SortDirection.DESCENDING`               |
| `after_date`  | Return entries after this date  | Must use with `sort=SortDirection.ASCENDING`                |
| `limit`       | Maximum items per page          | Varies by endpoint (10-100)                                 |
| `offset`      | Starting position               | Usually only `0` is supported                               |
| `sort`        | Sort direction                  | Use `SortDirection.ASCENDING` or `SortDirection.DESCENDING` |

## Endpoint-Specific Notes

Each paginated endpoint has specific constraints:

### `get_sleep_log_list`

- Max limit: 100 entries per page
- Date filtering: `before_date` or `after_date` (must specify one but not both)

### `get_activity_log_list`

- Max limit: 100 entries per page
- Date filtering: `before_date` or `after_date` (must specify one but not both)

### `get_ecg_log_list` and `get_irn_alerts_list`

- Max limit: 10 entries per page
