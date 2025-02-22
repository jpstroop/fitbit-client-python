# Logging

The Fitbit client implements a dual-logger system consisting of an **application
logger** and a **data logger**. These loggers serve different purposes and
handle different types of information.

## Logger Types

### Application Logger

The application logger (`fitbit_client.*`) handles operational logging
including:

- API request/response information
- Error conditions and exceptions
- Authentication flows
- General operational status

### Data Logger

The data logger (`fitbit_client.data`) specifically tracks important data fields
from successful API responses, including:

- IDs for resources (logs, activities, foods, etc.)
- Timestamps
- Device IDs
- Other critical reference fields

## Log Levels

The application logger uses multiple log levels:

- **DEBUG**: Detailed request/response information and authentication flow
  details

  ```
  DEBUG [fitbit_client.oauth] Initializing OAuth handler
  DEBUG [fitbit_client.callback_server] Starting HTTPS server on localhost:8080
  DEBUG [fitbit_client.callback_server] Generated private key
  DEBUG [fitbit_client.callback_server] Server thread started
  DEBUG [fitbit_client.callback_handler] Received callback request: /callback?code=...
  DEBUG [fitbit_client.callback_handler] Query parameters: {'code': [...], 'state': [...]}
  DEBUG [fitbit_client.callback_handler] OAuth callback received and validated successfully
  DEBUG [fitbit_client.oauth] Authentication token exchange completed successfully
  ```

  Setting log level to DEBUG is particularly useful when troubleshooting
  authentication issues as it provides detailed visibility into the OAuth2 flow,
  callback server operation, and token management.

- **INFO**: Successful operations and important state changes

  ```
  INFO [fitbit_client.ActivityResource] get_activity_goals succeeded for activities/goals/daily.json (status 200)
  ```

- **ERROR**: Failed operations, API errors, and exceptions

  ```
  ERROR [fitbit_client.ActivityResource] InvalidRequestException: Invalid parameter value (status: 400) [Type: invalid_request]
  ```

The data logger uses INFO level for all entries, with a structured JSON format:

```json
{
  "timestamp": "2025-02-17T06:45:13.798603",
  "method": "create_food",
  "fields": {
    "food.defaultUnit.id": 304,
    "food.defaultUnit.name": "serving",
    "food.foodId": 822139705,
    "food.name": "Breakfast Chia Pudding",
    "food.servings[0].unit.id": 304,
    "food.servings[0].unit.name": "serving",
    "food.servings[0].unitId": 304
  }
}
```

As you can see, this is really just summary of the response body that makes it
easy to get back in information you may not have captured in a one-off script.

Note that the log will not be valid JSON file, but each line will be a valid
object and it is be trivial to read it in at as `List[Dict[str, Any]]`.

## Important Fields

The data logger automatically tracks fields defined in
`IMPORTANT_RESPONSE_FIELDS`:

- access
- date
- dateTime
- deviceId
- endTime
- foodId
- id
- logId
- mealTypeId
- name
- startTime
- subscriptionId
- unitId

## Configuring Logging

To configure logging in your application:

```python
from logging import getLogger, StreamHandler, FileHandler, Formatter

# Configure application logger
app_logger = getLogger("fitbit_client")
formatter = Formatter("[%(asctime)s] %(levelname)s [%(name)s] %(message)s")

# Add handlers as needed (file and/or console)
handler = StreamHandler()  # or FileHandler("fitbit.log")
handler.setFormatter(formatter)
app_logger.addHandler(handler)
app_logger.setLevel("INFO")  # or "DEBUG" for verbose output

# Configure data logger
data_logger = getLogger("fitbit_client.data")
data_handler = FileHandler("fitbit_data.log")
data_handler.setFormatter(Formatter("%(message)s"))  # Raw JSON format
data_logger.addHandler(data_handler)
data_logger.setLevel("INFO")
data_logger.propagate = False  # Prevent duplicate logging
```

## Error Logging

The client automatically logs all API errors with rich context including:

- Error type and message
- HTTP status code
- Affected resource/endpoint
- Field-specific validation errors
- Raw error response when available
