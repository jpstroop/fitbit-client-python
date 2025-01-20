# resources/base.py
# Standard library imports
from typing import Any
from typing import Dict
from typing import Optional

# Third party imports
from requests import Response
from requests_oauthlib import OAuth2Session
from requests import HTTPError


class BaseResource:
    """
    Base class for all Fitbit API resources

    The Fitbit API has two types of endpoints:
    1. Public endpoints: /{endpoint}
       Used for database-wide operations like food search
    2. User endpoints: /user/{user_id}/{endpoint}
       Used for user-specific operations like logging food
    """

    API_BASE: str = "https://api.fitbit.com/1"

    def __init__(self, oauth_session: OAuth2Session, locale: str, language: str) -> None:
        self.headers: Dict = {"Accept-Locale": locale, "Accept-Language": language}
        self.oauth: OAuth2Session = oauth_session

    def _build_url(self, endpoint: str, user_id: str = "-", requires_user_id: bool = True) -> str:
        """
        Build full API URL with support for both public and user-specific endpoints.

        By default, endpoints are assumed to be user-specific. Set requires_user_id=False
        for public endpoints that operate on Fitbit's global database rather than
        user-specific data.

        Parameters:
            endpoint: API endpoint path
            user_id: User ID, defaults to '-' for authenticated user
            requires_user_id: Whether the endpoint requires user_id in the path

        Returns:
            Complete API URL
        """
        endpoint = endpoint.strip("/")

        if requires_user_id:
            return f"{self.API_BASE}/user/{user_id}/{endpoint}"
        return f"{self.API_BASE}/{endpoint}"

    def _make_request(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        user_id: str = "-",
        requires_user_id: bool = True,
        http_method: str = "GET",
    ) -> Dict[str, Any]:
        """
        Make a request to Fitbit API

        Parameters:
            endpoint: API endpoint path
            params: Optional query parameters
            data: Optional form data
            user_id: User ID, defaults to '-' for authenticated user
            requires_user_id: Whether the endpoint is user-specific (default: True)
            http_method: GET (default), POST, or DELETE

        Returns:
            JSON with two keys: "headers" and "content"
        """
        url: str = self._build_url(endpoint, user_id, requires_user_id)
        response: Response = self.oauth.request(
            http_method, url, data=data, json=json, params=params, headers=self.headers
        )
        try:
            response.raise_for_status()
        except HTTPError as e:
            e.add_note(response.text)
            raise
        full_response = {"headers": dict(response.headers), "content": response.json()}
        return full_response
