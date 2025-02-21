# Logging

There are two logs available: the **application log** and the **data log**. The
application log records interactions with the API including detailed error
information and request status. The data log records important data fields like
IDs for foods, food logs, and activity logs that the client creates.

The data log adds a little extra complexity, but it should be easy enough to
understand if you are familiar with Python's standard
[logging library](https://docs.python.org/3/library/logging.html#).

Here's a simple example of what you might put in your application:

```python
from logging import FileHandler
from logging import getLogger
from logging import INFO
from logging import StreamHandler
from logging import DEBUG


# Configure application logging
app_logger = getLogger("fitbit_client")
app_formatter = Formatter("[%(asctime)s] %(levelname)s [%(name)s] %(message)s")

# Add file handler for application logging
file_handler = FileHandler("logs/fitbit_app.log")
file_handler.setFormatter(app_formatter)
app_logger.addHandler(file_handler)

# Add console handler for application logging
console_handler = StreamHandler(stdout)
console_handler.setFormatter(app_formatter)
app_logger.addHandler(console_handler)

app_logger.setLevel(INFO)  # Set to DEBUG for detailed request information

# Configure data logging separately (file only, no console output)
data_logger = getLogger("fitbit_client.data") 
data_handler = FileHandler("logs/fitbit_data.log")
data_handler.setFormatter(Formatter("%(message)s"))  # Raw JSON format
data_logger.addHandler(data_handler)
data_logger.setLevel(INFO)
data_logger.propagate = False
```

The client provides logging at different levels:

Debug level shows comprehensive details for every API call:

```
[2025-01-27 23:37:09,660] DEBUG [fitbit_client.NutritionResource] API Call Details:
Endpoint: foods/log/favorite.json
Method: get_favorite_foods
Status: 200
Parameters: {}
Headers: {'Content-Type': 'application/json'}
Response: {'content': {'foods': [...]}}
```

All responses are logged at INFO level:

```
[2025-01-27 23:37:09,660] INFO [fitbit_client.NutritionResource] get_favorite_foods succeeded for foods/log/favorite.json (status 200)
[2025-01-27 23:39:27,703] INFO [fitbit_client.NutritionResource] Request failed for foods/log/favorite.json (status 404): [validation] resource owner: Invalid ID
```

Failures (4xx and 5xx responses) are additionally logged at ERROR level:

```
[2025-01-27 23:39:27,703] ERROR [fitbit_client.NutritionResource] Request failed for foods/log/favorite.json (status 404): [validation] resource owner: Invalid ID
```
