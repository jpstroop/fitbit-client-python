# Project TODO and Notes

## TODO
  - [ ] Check that all methods are implemented
    - [ ] Implement "Add Favorite Food" in nutrition
  - [x] Implement `accept-language` and `add-locale`
  - [ ] Map scopes to classes for documentation (this is not done consistently) and link to documentation at the method level:
    - [ ] activezone.py
    - [ ] activity.py
    - [ ] activity_timeseries.py
    - [ ] base.py
    - [ ] body.py
    - [ ] body_timeseries.py
    - [ ] breathingrate.py
    - [ ] cardio_fitness.py
    - [ ] constants.py
    - [ ] device.py
    - [ ] ecg.py
    - [ ] friends.py
    - [ ] heartrate_timeseries.py
    - [ ] heartrate_variability.py
    - [ ] irregular_rhythm.py
    - [x] nutrition.py
    - [ ] nutrition_timeseries.py
    - [ ] sleep.py
    - [ ] spo2.py
    - [ ] subscription.py
    - [ ] temperature.py
    - [ ] user.py
  - [ ] Add a note to the README that IntraDate is not implemented
  - [ ] Have isort add comments about imports
  - [ ] Add input validation for update methods
  - [ ] Add proper error handling; consider any custom exceptions
  - [ ] local logging since we can't implement intraday. In JSON?


## Testing
 * Is this worth it since it's all API? If so:
  - [ ] Add pytest configuration
  - [ ] Add test fixtures
  - [ ] Setup VCR.py for API mocking

* Test Coverage
  - [ ] Unit tests for each resource
  - [ ] Integration tests
  - [ ] Authentication flow tests
  - [ ] Error handling tests

## CI/CD
* GitHub Actions Setup
  - [x] Linting (black, isort)
  - [ ] Type checking (mypy)
  - [ ] Test running (TBD)
  - [ ] Coverage reporting (TBD)
  - [ ] Automated PyPI deployment

## Documentation
* API Documentation
  - [x] Document request payloads for each endpoint
  - [ ] Document response payloads for each endpoint
  - [ ] Add examples for complex operations
  - [ ] Document rate limiting behavior
  - [ ] Add authentication troubleshooting guide

* Development Documentation
  - [ ] Contributing guidelines
  - [ ] Development environment setup
  - [ ] Testing guide TBD

## CLI Tool
* Basic Implementation
  - [ ] Command structure design
  - [ ] Authentication handling
  - [ ] Output formatting

* Features
  - [ ] Resource CRUD operations
  - [ ] Data export capabilities
  - [ ] Configuration management
  - [ ] Profile switching?


  