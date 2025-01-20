# Project TODO and Notes

## TODO

- [x] `Move `client.py`` into a folder so that no code is at the top of the
  project.
- [x] Refactor BaseResource to just have one request method and parameterize the
  header. They all do the same thing otherwise.
- [x] Make all responses a `{ }` with two keys: `headers` and `response`
  - Allows for complete isolation of HTTP
  - Makes typing more reliable.
- [x] Implement `accept-language` and `add-locale`
- [x] Add a note to the README that IntraDate is not implemented
- [x] Have isort add comments about imports
- [ ] add `body.txt` to the message when we `raise_for_status()` in base.by
- [ ] can we add other units when using `create_food`? see note under `create_food_log`.
- [ ] Add input validation for update methods
- [ ] More robust and error handling; consider custom exceptions. Do everything
  we can to encapsulate HTTP errors
- [ ] Local logging since we can't implement intraday. In JSON?
- [ ] PyPI deployment
- [ ] ?PRIVATE filters on methods that return PUBLIC and PRIVATE stuff (API doesn't seem to have this) 
- [ ] Enum for units (it'll be big)
- [ ] ?`helpers` module. Things it could do:
  - Delete all history before a certain date
  - More detailed food reports (e.g. all nutrition for one day or week or last n days)
  - Different formats 

## Testing

TBD - the most useful thing would be to test that the requests are built 
correctly - the correct method, params, body etc.

- Is this worth it since it's all API? If so:

  - [ ] Add pytest configuration
  - [ ] Add test fixtures
  - [ ] Set up VCR.py for API mocking

- Test Coverage

  - [ ] Unit tests for each resource
  - [ ] Integration tests
  - [ ] Authentication flow tests
  - [ ] Error handling tests

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

## Documentation:
  - [ ] `activezone.py`
    - [ ] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `activity.py`
    - [x] Add scope to class docstring
    - [x] Link to documentation at the method level
    - [x] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [x] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [x] Ensure method names match endpoint name
  - [ ] `activity_timeseries.py`
    - [ ] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `base.py`
    - [ ] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `body.py`
    - [ ] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `body_timeseries.py`
    - [ ] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `breathingrate.py`
    - [ ] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `cardio_fitness.py`
    - [ ] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `constants.py`
    - [ ] Note which classes/methods use each Enum
  - [ ] `device.py`
    - [ ] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `ecg.py`
    - [ ] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `friends.py`
    - [ ] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `heartrate_timeseries.py`
    - [ ] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `heartrate_variability.py`
    - [ ] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `irregular_rhythm.py`
    - [ ] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `nutrition.py`
    - [x] Add scope to class docstring
    - [x] Link to documentation at the method level
    - [x] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [x] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `nutrition_timeseries.py`
    - [ ] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `sleep.py`
    - [ ] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `spo2.py`
    - [ ] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `subscription.py`
    - [ ] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `temperature.py`
    - [ ] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
  - [ ] `user.py`
    - [x] Add scope to class docstring
    - [ ] Link to documentation at the method level
    - [ ] Check "Notes" from docstrings; they mostly just repeat the fitbit API docs
    - [ ] Double Check that all methods are implemented
    - [ ] Document response payloads, or at least what to expect, for each endpoint
    - [ ] Ensure method names match endpoint name
