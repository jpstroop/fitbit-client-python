# Project TODO and Notes

## TODO

- [ ] Complete coverage

- [ ] Get rid of deprecation warnings from test coverage

- [ ] Finish method naming and typing documentation.

- [ ] Confront MyPy. See https://stackoverflow.com/a/51294709 for json help

- [ ] When typing resource, wrap the actual response type around the JSONType,,
  e.g. List[JSONType], Dict[str, JSONType], so that the user can actually know
  what to expect (or None, of course)

- [ ] Test that all methods have an alias in `Client` and that the signatures
  match

- [ ] Rationalize `ClientValidationException` subclass inheritance

- [ ] Set up CI!

- [ ] Consider a "replace_food_log" helper that does a delete + an add in one.
  (there might be several of these that make sense--just take an ID and then the
  signature of the "create" method)

- Docs! https://www.sphinx-doc.org/en/master/#get-started (put on github pages?)

- [ ] Why does this log twice:

```log
[2025-02-07 16:41:38,471] ERROR [fitbit_client.NutritionResource] ValidationException: Intensity level "MEDIUM" available only if weight objective is to lose weight. [Type: validation, Status: 400], Field: intensity
[2025-02-07 16:41:38,472] ERROR [fitbit_client.NutritionResource] ValidationException in create_food_goal for foods/log/goal.json: Intensity level "MEDIUM" available only if weight objective is to lose weight.

```

- [ ] For methods with paging, figure out how to encapsulate it...do they call
  `_make_request` with the URL in the response, or what? Does the response
  return a 2-tuple where the first item is the response and second is a
  pre-baked function that can me called? See:
  https://g.co/gemini/share/ce142f7e323a

  - Implement as `(response, page_forward, page_backward)` so that the user can
    use the names `next_page` and `previous_page`, eg.
    `next_page = page_forward()`
  - hopefully we can put this is `utils/page_helper.py` somehow, so that it can
    be reused.
  - We may need a public version of a generic `make_request` method.

- [ ] For all `create_...`methods, add the ID from the response to logs and
  maybe something human readable, like the first n characters of the name??.
  Right now:

```log
[2025-02-05 06:09:34,828] INFO [fitbit_client.NutritionResource] create_food_log succeeded for foods/log.json (status 201)
```

- [ ] Review and add link to
  https://dev.fitbit.com/build/reference/web-api/developer-guide/best-practices/
  in README--they still apply!

- [ ] Form to change scopes are part of OAuth flow? Maybe get rid of the cut and
  paste method altogether? It's less to test...

- [ ] Make the food download_food_logs (rename to `get_food_logs`) and food log
  to CSV part of one helper package. It should expand the foods to have their
  complete nutrition (a separate call for each unique food) (put this in a
  `tools` package??)

- [ ] PyPI deployment

- [ ] Extension: PRIVATE filters on methods that return PUBLIC and PRIVATE stuff
  (API doesn't seem to have this). Maybe a sidecar database?

- [ ] Enum for units? (it'll be big, maybe just common ones?)

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
