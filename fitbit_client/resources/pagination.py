# fitbit_client/resources/pagination.py

# Standard library imports
from collections.abc import Iterator
import logging
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Set
from typing import TYPE_CHECKING

# Local imports
from fitbit_client.utils.types import JSONDict

# Set up logging
logger = logging.getLogger(__name__)

# Avoid circular imports
if TYPE_CHECKING:
    # Local imports
    from fitbit_client.resources.base import BaseResource


class PaginatedIterator(Iterator[JSONDict]):
    """Iterator for paginated Fitbit API responses.

    This class provides a Pythonic iterator interface to paginated API responses,
    allowing users to iterate through all pages without manually handling pagination.
    
    It uses the 'next' URL provided in the pagination metadata to fetch subsequent pages,
    automatically stopping when there are no more pages.

    Example:
        ```python
        # Get an iterator for sleep log pages
        sleep_iterator = client.get_sleep_log_list(
            before_date="2025-01-01",
            sort=SortDirection.DESCENDING,
            as_iterator=True
        )

        # Iterate through all pages
        for page in sleep_iterator:
            for sleep_entry in page["sleep"]:
                print(sleep_entry["logId"])
        ```
    """

    def __init__(
        self, 
        response: JSONDict,
        endpoint: str,
        method_params: Dict[str, Any],
        fetch_next_page: Callable[[str, Dict[str, Any]], JSONDict]
    ) -> None:
        """Initialize a paginated iterator.

        Args:
            response: The initial API response containing pagination information
            endpoint: The API endpoint path
            method_params: The original parameters used for the request
            fetch_next_page: Callback function that takes an endpoint and params and returns the next page
        """
        self._initial_response = response
        self._endpoint = endpoint
        self._method_params = method_params.copy()
        self._fetch_next_page = fetch_next_page
        
        # This flag helps us keep track of whether we've returned the initial page
        self._returned_initial = False
        
        # Find the data key in this response
        self._data_key = self._get_data_key(response)
        
        # Track seen IDs to prevent duplicate data
        self._seen_ids = set()
        self._track_ids(response)
        
        # Keep reference to the last page we've seen
        self._last_page = response
        
    def _get_data_key(self, response: JSONDict) -> Optional[str]:
        """Find the key in the response that contains the data array.
        
        Args:
            response: The API response
            
        Returns:
            The data key if found, None otherwise
        """
        # Common data keys in Fitbit API responses
        data_keys = ["sleep", "activities", "ecgReadings", "alerts"]
        
        for key in data_keys:
            if isinstance(response.get(key), list):
                return key
                
        return None
        
    def _find_id_field(self, items: list) -> Optional[str]:
        """Find the ID field used in items.
        
        Args:
            items: List of data items
            
        Returns:
            The ID field name if found, None otherwise
        """
        if not items:
            return None
            
        # Common ID fields in Fitbit API responses (in order of preference)
        id_fields = ["logId", "id", "activityId", "ecgReadingId", "readingId", "alertId"]
        
        for field in id_fields:
            if field in items[0]:
                return field
                
        return None
        
    def _get_safe_id(self, item: Dict[str, Any]) -> str:
        """Get a reliable ID from an item, even if standard ID fields are missing.
        
        Args:
            item: Data item to extract ID from
            
        Returns:
            String ID (either from a standard field or a generated hash)
        """
        # Try standard ID fields
        id_field = self._find_id_field([item])
        if id_field and item.get(id_field) is not None:
            return str(item[id_field])
            
        # Try other possible ID fields
        for field in ["logId", "id", "activityId", "ecgReadingId", "readingId", "alertId"]:
            if field in item and item[field] is not None:
                return str(item[field])
                
        # Generate a hash-based ID from the item as last resort
        # This ensures we can still track the item for duplicate detection
        import hashlib
        item_str = str(sorted(item.items()))
        return hashlib.md5(item_str.encode()).hexdigest()
        
    def _track_ids(self, response: JSONDict) -> None:
        """Track IDs in the response to detect duplicates.
        
        Args:
            response: The API response
        """
        # If no data key or no data, nothing to track
        if not self._data_key or not response.get(self._data_key):
            return
            
        items = response[self._data_key]
        if not items:
            return
            
        # Add new IDs to the set
        new_ids = 0
        for item in items:
            # Get a reliable ID for this item
            item_id = self._get_safe_id(item)
            
            # Track if this is a new ID
            if item_id not in self._seen_ids:
                self._seen_ids.add(item_id)
                new_ids += 1
                    
        if new_ids:
            logger.debug(f"Added {new_ids} new IDs. Total tracked: {len(self._seen_ids)}")
        
    def _has_new_data(self, response: JSONDict) -> bool:
        """Check if the response contains any new data we haven't seen.
        
        Args:
            response: The API response
            
        Returns:
            True if the response contains new data, False otherwise
        """
        # If no data key or no data, no new data
        if not self._data_key or not response.get(self._data_key):
            return False
            
        items = response[self._data_key]
        if not items:
            return False
            
        # Check if any item has an ID we haven't seen
        for item in items:
            item_id = self._get_safe_id(item)
            if item_id not in self._seen_ids:
                return True
                
        return False
        
    def _get_next_params(self) -> Optional[Dict[str, Any]]:
        """Get parameters for the next page request.
        
        Returns:
            Parameters for the next page, or None if there is no next page
        """
        # Check if we have a pagination block with a next URL
        pagination = self._last_page.get("pagination", {})
        next_url = pagination.get("next")
        
        # If there's no next URL, there's no next page
        if not next_url:
            logger.debug("No 'next' URL in pagination, reached end of pages")
            return None
            
        # Extract query parameters from the next URL
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(next_url)
        
        # Parse the query string into a dictionary
        # parse_qs returns values as lists, so we need to extract the first item
        query_params = {k: v[0] if v else "" for k, v in parse_qs(parsed_url.query).items()}
        
        logger.debug(f"Using parameters from 'next' URL: {query_params}")
        return query_params
    
    def __iter__(self) -> "PaginatedIterator":
        """Return self as an iterator.
        
        Returns:
            Self
        """
        self._returned_initial = False
        return self
        
    def __next__(self) -> JSONDict:
        """Get the next page from the paginated response.
        
        Returns:
            The next page of results
            
        Raises:
            StopIteration: When there are no more pages
        """
        # If this is the first call to next(), return the initial response
        if not self._returned_initial:
            logger.debug("Returning initial page")
            self._returned_initial = True
            return self._initial_response
            
        # Try to get the next page
        try:
            # Get parameters for the next request from the 'next' URL
            next_params = self._get_next_params()
            
            # If there are no next parameters, we've reached the end
            if next_params is None:
                logger.debug("No more pages available")
                raise StopIteration
            
            # Make the request
            logger.debug(f"Fetching next page with params from 'next' URL")
            next_page = self._fetch_next_page(self._endpoint, next_params)
            
            # Check if we got a valid response with data
            if not isinstance(next_page, dict):
                logger.debug("Invalid response, stopping pagination")
                raise StopIteration
                
            # Track IDs in the new page (for duplicate detection)
            self._track_ids(next_page)
            
            # Save this page for the next iteration
            self._last_page = next_page
            
            return next_page
        except Exception as e:
            logger.error(f"Error during pagination: {str(e)}")
            raise StopIteration
            
    @property
    def initial_response(self) -> JSONDict:
        """Get the initial response.
        
        Returns:
            The initial API response
        """
        return self._initial_response


def create_paginated_iterator(
    response: JSONDict, 
    resource: "BaseResource", 
    endpoint: str,
    method_params: Dict[str, Any],
    debug: bool = False
) -> PaginatedIterator:
    """Create a paginated iterator from a response.

    Args:
        response: The initial API response containing pagination information
        resource: The resource instance that made the original request
        endpoint: The API endpoint path
        method_params: The original parameters used for the request
        debug: Whether to enable debug mode for subsequent requests

    Returns:
        A PaginatedIterator instance
    """
    # Ensure the response has a pagination object
    if "pagination" not in response:
        response["pagination"] = {}
        
    # Define a callback to fetch the next page
    def fetch_next_page(endpoint: str, params: Dict[str, Any]) -> JSONDict:
        try:
            result = resource._make_request(
                endpoint=endpoint,
                params=params,
                debug=debug
            )
            
            # Ensure the result is a valid dictionary
            if not isinstance(result, dict):
                return {}
                
            # Ensure result has a pagination object
            if "pagination" not in result:
                result["pagination"] = {}
                
            return result
        except Exception as e:
            logger.error(f"Error fetching page: {str(e)}")
            return {}

    return PaginatedIterator(response, endpoint, method_params, fetch_next_page)