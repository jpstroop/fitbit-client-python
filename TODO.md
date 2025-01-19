# Project TODO and Notes

## TODO
- [ ] Move `client.py` into a folder so that no code is at the top of the project.
  - Should it go into `client/__init__.py`?
- Implement `all` in `__init__.py`s?
- [ ] Make all responses a `{ }` with two keys: `headers` and `response`
  - Allows for complete isolation of HTTP
  - Makee typing more reliable.
- [ ] Check that all methods are implemented
  - [ ] Implement "Add Favorite Food" in nutrition
- [x] Implement `accept-language` and `add-locale`
- [ ] Map scopes to classes for documentation (this is not done consistently) _AND_ link to
  documentation at the method level:
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
- [x] Add a note to the README that IntraDate is not implemented
- [x] Have isort add comments about imports
- [ ] Add input validation for update methods
- [ ] More robust error handling; consider custom exceptions
- [ ] local logging since we can't implement intraday. In JSON?

## Testing

TBD

- Is this worth it since it's all API? If so:

  - [ ] Add pytest configuration
  - [ ] Add test fixtures
  - [ ] Setup VCR.py for API mocking

- Test Coverage

  - [ ] Unit tests for each resource
  - [ ] Integration tests
  - [ ] Authentication flow tests
  - [ ] Error handling tests

## CI/CD

- GitHub Actions Setup
  - [ ] Linting
    - [x] black
    - [x] isort
    - [x] mdformat
    - [ ] mypy
  - [ ] Test running (TBD)
  - [ ] Coverage reporting (TBD)
  - [ ] Automated PyPI deployment

## Documentation

- API Documentation

  - [x] Document request payloads for each endpoint
  - [ ] Document response payloads for each endpoint
  - [ ] Add examples for complex operations
  - [ ] Document rate limiting behavior
  - [x] Badges
    - [x] Black
    - [x] Python 3.13
    - [x] License

- Development Documentation

  - [x] Contributing guidelines
  - [x] Development environment setup
  - [ ] Testing guide TBD

## CLI Tool

- Basic Implementation

  - [ ] Command structure design
  - [ ] Authentication handling
  - [ ] Output formatting

- Features

  - [ ] Resource CRUD operations
  - [ ] Data export capabilities
  - [ ] Configuration management
  - [ ] Profile switching?
