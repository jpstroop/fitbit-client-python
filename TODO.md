# Project TODO and Notes

## TODO

- [ ] Review and add link to
  https://dev.fitbit.com/build/reference/web-api/developer-guide/best-practices/
  in README--they still apply!

- [ ] Why does the auth flow log this twice:

  ```log
  [2025-01-30 21:24:53,958] INFO [fitbit_client] Authentication successful
  [2025-01-30 21:24:53,958] INFO [fitbit_client] Authentication successful
  ```

- [ ] Validation to NutritionResource - Calories must be ints, not floats like
  everything else

- [ ] Make sure all IDs (`water_log_id`, `food_id`, `unit_id`, etc.) are typed
  as ints across all resources

- [ ] More robust and error handling; consider custom exceptions. Do everything
  we can to encapsulate HTTP errors. See
  https://dev.fitbit.com/build/reference/web-api/troubleshooting-guide/error-handling/

- [ ] Response validation? Accidentally doing a GET instead of a POST on, e.g.
  `food.json` will yield a response, but not the one you want!

- [ ] Confront MyPy

- [ ] Tests that all methods have an alias and that the signatures match

- [ ] Do other (non-standard) nutrients show up in food_logs?

- [ ] `raise NotImplementedError` for intraday methods (add stubs)

- [ ] Consider not supporting the Subscription and /or Friends endpoints either?

- [ ] Figure out throttling when making multiple requests.

  - Can we make this more elegant than just putting in explict `sleep(1.0)`
    statements as needed?
  - Can we handle it and retry a few times before erroring out?

- [ ] If we are logging HTTP headers and status, maybe we should go back to the
  API response without wrapping it in a dict? * Could have two \_make_request
  methods to handle typing between [] and {} ?

- [ ] Why does `delete_custom_food` say "Invalid foodId: .." for my foods?

  - Are _any_ delete methods working? NOTE: they may have worked once. TRY AGAIN
    - `delete_favorite_food` :
      ```json
      {
        "errorType": "validation",
        "fieldName": "foodId",
        "message": "Error removing food from favorites. Food is currently not a favorite: 821261353"
      }
      ```
    - `delete_water_log` :
      ```json
      {
        "errorType": "validation",
        "fieldName": "waterId",
        "message": "Invalid water id: 9988944308"
      }
      ```

- [ ] Add input validation for update methods

- [ ] PyPI deployment

- [ ] Extension: ?PRIVATE filters on methods that return PUBLIC and PRIVATE
  stuff (API doesn't seem to have this)

- [ ] Enum for units? (it'll be big)

- [ ] ?`helpers` module. Things it could do:

  - Delete all history before a certain date
  - More detailed food reports (e.g. all nutrition for one day or week or last n
    days)
  - Serializing in different formats, e.g. CSV, .md?

## Testing

TODO: test that the requests are built correctly - the correct method, params,
body etc.

## CI/CD/Linting

- [ ] Linting

  - [x] black
  - [x] isort
  - [x] mdformat
  - [ ] mypy

- GitHub Actions Setup

  - [ ] Linting
    - [ ] black
    - [ ] isort
    - [ ] mdformat
    - [ ] mypy
  - [ ] Test running (TBD)
  - [ ] Coverage reporting (TBD)
  - [ ] Automated PyPI deployment

## CLI Tool

??

- Basic Implementation

  - [ ] Configuration
  - [ ] Command structure design
  - [ ] Authentication handling
  - [ ] Output formatting

- Features

  - [ ] Resource CRUD operations
  - [ ] Data export capabilities
  - [ ] Configuration management
  - [ ] Profile switching?
