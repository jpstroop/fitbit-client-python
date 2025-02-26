# Project TODO and Notes

## Refactoring TODOs

- Typing

  - Try to get rid of `Optional[Dict[str, Any]]` args

- base.py: reorganize and see what we can move out.

  - Rename to `_base`? Files it first, makes it clearer that everything in it is
    private
  - Move the methods for building `curl` commands into a mixin? It's a lot of
    code for an isolated and tightly scoped feature.
  - refactor `_make_request`.
    - do we need both `data` and `json`? Also, could we simplify a lot of typing
      if we separated GET, POST, and DELETE methods? Maybe even a separate,
      second non-auth GET? Could use `@overload`
    - we had to makee a `ParamDict` type in `nutrition.py`. Use this everywhere?
    - start by looking at how many methods use which params

- client.py:

  - Creat and Test that all methods have an alias in `Client` and that the
    signatures match
  - Make sure that `ClientValidationException` is getting used for arbitrary
    validations like:

```python
if not food_id and not (food_name and calories):
    raise ClientValidationException(
        "Must provide either food_id or (food_name and calories)"
    )
```

- exceptions.py

  - Should ClientValidationException really subclass FitbitAPIException? It
    doesn't need the API lookup mapping (`exception_type`) or a `status_code`,
    so we may just be able to simplify it. The most important thing is that the
    user understands that the message came from the client prior to the API
    call.

- Resource docstrings/documentation:

  - Update the list of exceptions that are raised in the doctring for
    `base._make_request`
  - Review all documentation and between **API docs, return types, and
    exceptions**, update the doctrings
  - Update "Returns" in all resource docstrings
  - Review and add link to
    https://dev.fitbit.com/build/reference/web-api/developer-guide/best-practices/
    in README--they still apply!

- Set up CI!

## Longer term TODOs

- Performance profiling

- Docs! https://www.sphinx-doc.org/en/master/#get-started (put on github pages?)

- Why does this log twice:

```log
[2025-02-07 16:41:38,471] ERROR [fitbit_client.NutritionResource] ValidationException: Intensity level "MEDIUM" available only if weight objective is to lose weight. [Type: validation, Status: 400], Field: intensity
[2025-02-07 16:41:38,472] ERROR [fitbit_client.NutritionResource] ValidationException in create_food_goal for foods/log/goal.json: Intensity level "MEDIUM" available only if weight objective is to lose weight.

```

- For methods with paging, figure out how to encapsulate it...do they call
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

- For all `create_...`methods, add the ID from the response to logs and maybe
  something human readable, like the first n characters of the name??. Right
  now:

```log
[2025-02-05 06:09:34,828] INFO [fitbit_client.NutritionResource] create_food_log succeeded for foods/log.json (status 201)
```

- Form to change scopes are part of OAuth flow? Maybe get rid of the cut and
  paste method altogether? It's less to test...

- Extension ideas:

  - Make the food download_food_logs method (rename to `get_food_logs`) and food
    log to CSV part of one helper package. It should expand the foods to have
    their complete nutrition (a separate call for each unique food) (put this in
    a `tools` package??)
  - PRIVATE filters on methods that return PUBLIC and PRIVATE stuff (API doesn't
    seem to have this). Would require a sidecar database or pickle - it just
    needs to be a hash with a few elements to facilitate a lookup via the api
  - Consider e.g., a "replace_food_log" extension that does a delete + an add in
    one. (there might be several of these that make sense--just take an ID and
    then the signature of the "create" method).

- PyPI deployment

- Enum for units? (it'll be big, maybe just common ones?)

## CI/CD/Linting

- GitHub Actions Setup

  - Linting
    - black
    - isort
    - mdformat
    - mypy
  - Test running (TBD)
  - Coverage reporting (TBD)
  - Automated PyPI deployment
