# resources/base.py
from typing import Any
from typing import Dict
from typing import Optional

from requests import Response
from requests_oauthlib import OAuth2Session


class BaseResource:
    """Base class for all Fitbit API resources"""

    API_BASE: str = "https://api.fitbit.com"
    API_VERSION: str = "1.2"  # Fitbit API version

    def __init__(self, oauth_session: OAuth2Session) -> None:
        self.oauth: OAuth2Session = oauth_session

    def _build_url(self, endpoint: str, user_id: str = "-") -> str:
        """
        Build full API URL

        Parameters:
            endpoint: API endpoint path
            user_id: User ID, defaults to '-' for authenticated user

        Returns:
            Complete API URL
        """
        # Remove leading/trailing slashes from endpoint
        endpoint = endpoint.strip("/")
        return f"{self.API_BASE}/{self.API_VERSION}/user/{user_id}/{endpoint}"

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, user_id: str = "-") -> Dict[str, Any]:
        """
        Make GET request to Fitbit API

        Parameters:
            endpoint: API endpoint path
            params: Optional query parameters
            user_id: User ID, defaults to '-' for authenticated user

        Returns:
            JSON response from the API

        Raises:
            requests.exceptions.HTTPError: If the request fails
        """
        url: str = self._build_url(endpoint, user_id)
        response: Response = self.oauth.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Make POST request to Fitbit API

        Parameters:
            endpoint: API endpoint path
            data: Optional form data
            json: Optional JSON data
            user_id: User ID, defaults to '-' for authenticated user

        Returns:
            JSON response from the API

        Raises:
            requests.exceptions.HTTPError: If the request fails
        """
        url: str = self._build_url(endpoint, user_id)
        response: Response = self.oauth.post(url, data=data, json=json)
        response.raise_for_status()
        return response.json()

    def _delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None, user_id: str = "-") -> None:
        """
        Make DELETE request to Fitbit API

        Parameters:
            endpoint: API endpoint path
            params: Optional query parameters
            user_id: User ID, defaults to '-' for authenticated user

        Raises:
            requests.exceptions.HTTPError: If the request fails
        """
        url: str = self._build_url(endpoint, user_id)
        response: Response = self.oauth.delete(url, params=params)
        response.raise_for_status()
