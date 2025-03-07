# API Method Naming Conventions

## Naming Principles

The method names in this library are designed to align with the official Fitbit
Web API Documentation. When there are inconsistencies in the official
documentation, we follow these principles:

1. The URL slug in the documentation is the primary reference
2. Method names always use underscores (snake_case), not camelCase
3. The HTTP verb is reflected in the method name prefix:
   - `get_`: For HTTP GET operations
   - `create_`: For HTTP POST operations that create new resources
   - `update_`: For HTTP PUT operations
   - `delete_`: For HTTP DELETE operations
   - `add_`: Only used in specific contexts where "add" is more intuitive than
     "create"

## API Documentation Alignment

For any discrepancies between different parts of the official documentation, we
prioritize the URL slug. For example, if the documentation page title says "Get
Time Series by Date" but the URL is ".../get-azm-timeseries-by-date/", our
method will be named `get_azm_timeseries_by_date()`.

This approach ensures consistent naming throughout the library and makes methods
easier to find based on the official documentation.

## Inconsistencies in the API

The Fitbit API contains several inconsistencies, which our method names
necessarily reflect:

- `create_activity_goals` creates only one goal at a time
- `add_favorite_foods` adds one food at a time, while all other creation methods
  use "create" prefix
- Some pluralized methods return lists, while others return dictionaries
  containing lists

## Method Aliases

For user convenience, some methods have aliases:

- `create_activity_goal` -> `create_activity_goals`
- `add_favorite_food` -> `add_favorite_foods`
- `create_favorite_food` -> `add_favorite_foods`
- `delete_favorite_food` -> `delete_favorite_foods`
- `create_sleep_goal` -> `create_sleep_goals`
- `get_sleep_goal` -> `get_sleep_goals`

These aliases help accommodate different expectations and ensure backward
compatibility.

## Resource Structure

The client organizes API endpoints into logical resource classes, each
representing a different section of the Fitbit API. For a complete list of all
methods and their return types, see
[TYPES.md](TYPES.md#method-return-types-reference).
