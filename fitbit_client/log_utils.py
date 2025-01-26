# fitbit_client/log_utils.py

# Standard library imports
from datetime import datetime
from functools import wraps
from inspect import currentframe
from inspect import getframeinfo
from json import dumps
from logging import getLogger
from typing import Any
from typing import Callable
from typing import Dict
from typing import Set

# Constants for important fields we want to track
IMPORTANT_RESPONSE_FIELDS: Set[str] = {
    "access",  # PUBLIC/PRIVATE/SHARED
    "date",  # Dates
    "dateTime",  # Timestamps
    "deviceId",  # Device IDs
    "endTime",  # Activity/sleep end times
    "foodId",  # Food resource IDs
    "id",  # Generic resource IDs
    "logId",  # Log entry IDs
    "mealTypeId",  # Type of Meal
    "name",  # Resource names
    "startTime",  # Activity/sleep start times
    "subscriptionId",  # Subscription IDs
    "unitId",  # Measurement unit IDs
}


def extract_important_fields(
    data: Dict[str, Any], fields: Set[str] = IMPORTANT_RESPONSE_FIELDS
) -> Dict[str, Any]:
    """Extract important fields from response data for logging."""
    extracted = {}

    def extract_recursive(d: Dict[str, Any], prefix: str = "") -> None:
        for key, value in d.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if key in fields:
                extracted[full_key] = value

            if isinstance(value, dict):
                extract_recursive(value, full_key)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        extract_recursive(item, f"{full_key}[{i}]")

    extract_recursive(data)
    return extracted


def log_response(func: Callable) -> Callable:
    """
    Decorator to handle both application and data logging for API responses.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the actual resource class and calling method
        resource = args[0]
        endpoint = args[1] if len(args) > 1 else "unknown"

        # Find the original caller by walking up the stack
        frame = currentframe()
        while frame:
            if frame.f_code.co_name != "_make_request" and frame.f_code.co_name != "wrapper":
                calling_method = frame.f_code.co_name
                break
            frame = frame.f_back

        # Get loggers - one for application logging, one for data tracking
        logger = getLogger(f"fitbit_client.{resource.__class__.__name__}")
        data_logger = getLogger("fitbit_client.data")

        try:
            # Execute the API call
            response = func(*args, **kwargs)

            if response and isinstance(response, dict):
                status = response.get("status")
                content = response.get("content", {})
                params = kwargs.get("params", {})

                # Detailed debug logging
                debug_msg = (
                    f"API Call Details:\n"
                    f"Endpoint: {endpoint}\n"
                    f"Method: {calling_method}\n"
                    f"Status: {status}\n"
                    f"Parameters: {params}\n"
                    f"Headers: {response.get('headers', {})}\n"
                    f"Response: {content}"
                )
                logger.debug(debug_msg)

                # Standard response logging at INFO level
                if (
                    isinstance(content, dict)
                    and "errors" in content
                    and isinstance(content["errors"], list)
                ):
                    error = content["errors"][0]
                    msg = (
                        f"Request failed for {endpoint} (status {status}): "
                        f"[{error['errorType']}] {error['fieldName']}: {error['message']}"
                    )
                    logger.info(msg)
                    if status >= 400:
                        logger.error(msg)
                else:
                    logger.info(f"{calling_method} succeeded for {endpoint} (status {status})")

                # Handle data logging for successful responses
                if status < 400 and isinstance(content, dict):
                    important_fields = extract_important_fields(content)
                    if important_fields:
                        data_entry = {
                            "timestamp": datetime.now().isoformat(),
                            "method": calling_method,
                            "fields": important_fields,
                        }
                        data_logger.info(dumps(data_entry))

            return response

        except Exception as e:
            logger.exception(f"Unexpected error in {calling_method} for {endpoint}: {str(e)}")
            raise

    return wrapper
