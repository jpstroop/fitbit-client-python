# Project TODO and Notes

## TODOs:

- be able to set scopes when initializing the client

- security notes

- PyPi deployment

- For all `create_...`methods, add the ID from the response to logs and maybe
  something human readable, like the first n characters of the name??. Right
  now:

```log
[2025-02-05 06:09:34,828] INFO [fitbit_client.NutritionResource] create_food_log succeeded for foods/log.json (status 201)
```

- base.py: reorganize and see what we can move out.

  - Rename to `_base`? Files it first, makes it clearer that everything in it is
    private

- client.py:

  - Creat and Test that all methods have an alias in `Client` and that the
    signatures match

- CI:

* Read and implement:
  https://docs.github.com/en/code-security/code-scanning/creating-an-advanced-setup-for-code-scanning/configuring-advanced-setup-for-code-scanning#configuring-advanced-setup-for-code-scanning-with-codeql

- exceptions.py Consider:
  - Add automatic token refresh for ExpiredTokenException
  - Implement backoff and retry for RateLimitExceededException
  - Add retry with exponential backoff for transient errors (5xx)

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

- Enum for units? (it'll be big, maybe just common ones?)
