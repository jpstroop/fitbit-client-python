# fitbit_client/resources/friends.py

# Standard library imports
from typing import cast

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.utils.types import JSONDict


class FriendsResource(BaseResource):
    """Provides access to Fitbit Friends API for retrieving social connections and leaderboards.

    This resource handles endpoints for accessing a user's friends list and leaderboard data,
    which shows step count rankings among connected users. The Friends API allows applications
    to display social features like friend lists and competitive step count rankings.

    API Reference: https://dev.fitbit.com/build/reference/web-api/friends/

    Required Scopes:
      - social: Required for all endpoints in this resource

    Note:
        The Fitbit privacy setting 'My Friends' (Private, Friends Only, or Public) determines
        the access to a user's list of friends. Similarly, the 'Average Daily Step Count'
        privacy setting affects whether a user appears on leaderboards.

        This scope does not provide access to friends' Fitbit activity data - those users need to
        individually consent to share their data with your application.

        This resource uses API version 1.1 instead of the standard version 1.
    """

    API_VERSION: str = "1.1"

    def get_friends(self, user_id: str = "-", debug: bool = False) -> JSONDict:
        """Returns a list of the specified Fitbit user's friends.

        This endpoint retrieves all social connections (friends) for a Fitbit user. It returns
        basic profile information for each friend, including their display name and profile picture.

        API Reference: https://dev.fitbit.com/build/reference/web-api/friends/get-friends/

        Args:
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: List of the user's Fitbit friends with basic profile information

        Raises:
            fitbit_client.exceptions.AuthorizationException: If the required scope is not granted
            fitbit_client.exceptions.ForbiddenException: If user's privacy settings restrict access

        Note:
            The user's privacy settings ('My Friends') determine whether this data is accessible.
            Access may be restricted based on whether the setting is Private, Friends Only, or Public.

            This endpoint uses API version 1.1, which has a different response format compared to
            most other Fitbit API endpoints.
        """
        result = self._make_request(
            "friends.json", user_id=user_id, api_version=FriendsResource.API_VERSION, debug=debug
        )
        return cast(JSONDict, result)

    def get_friends_leaderboard(self, user_id: str = "-", debug: bool = False) -> JSONDict:
        """Returns the user's friends leaderboard showing step counts for the last 7 days.

        This endpoint retrieves a ranked list of the user and their friends based on step counts
        over the past 7 days (previous 6 days plus current day in real time). This can be used
        to display competitive step count rankings among connected users.

        API Reference: https://dev.fitbit.com/build/reference/web-api/friends/get-friends-leaderboard/

        Args:
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Ranked list of the user and their friends based on step counts over the past 7 days

        Raises:
            fitbit_client.exceptions.AuthorizationException: If the required scope is not granted
            fitbit_client.exceptions.ForbiddenException: If user's privacy settings restrict access

        Note:
            - The leaderboard includes data for the previous 6 days plus the current day in real time
            - The authorized user (self) is included in the response
            - The 'Average Daily Step Count' privacy setting affects whether users appear on leaderboards
            - Both active ('ranked-user') and inactive ('inactive-user') friends are included
            - Inactive users have no step-rank or step-summary values
            - The 'included' section provides profile information for all users in the 'data' section

            This endpoint uses API version 1.1, which has a different response format compared to
            most other Fitbit API endpoints.
        """
        result = self._make_request(
            "leaderboard/friends.json",
            user_id=user_id,
            api_version=FriendsResource.API_VERSION,
            debug=debug,
        )
        return cast(JSONDict, result)
