# fitbit_client/resources/friends.py

# Standard library imports
from typing import Any
from typing import Dict

# Local imports
from fitbit_client.resources.base import BaseResource


class FriendsResource(BaseResource):
    """
    Handles Fitbit Friends API endpoints for retrieving a user's friends list and leaderboard data.

    API Reference: https://dev.fitbit.com/build/reference/web-api/friends/

    Note:
        This resource requires the 'social' scope.
        The Fitbit privacy setting 'My Friends' (Private, Friends Only or Public) determines
        the access to a user's list of friends.
        This scope does not provide access to friends' Fitbit data - those users need to
        individually consent to share their data.
    """

    API_VERSION: str = "1.1"

    def get_friends(self, user_id: str = "-") -> Dict[str, Any]:
        """
        Retrieves a list of the specified Fitbit user's friends.

        Args:
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.

        Returns:
            A list of friend objects containing:
            - type: Type of the data ("person")
            - id: Fitbit user id
            - attributes:
                - avatar: Link to user's avatar picture
                - child: Boolean indicating if friend is a child account
                - friend: Boolean indicating if user is a friend
                - name: Person's display name

        Note:
            The user's privacy settings ('My Friends') determine whether this data is accessible.
            Access may be restricted based on whether the setting is Private, Friends Only, or Public.
        """
        return self._make_request(
            "friends.json", user_id=user_id, api_version=FriendsResource.API_VERSION
        )["data"]

    def get_friends_leaderboard(self, user_id: str = "-") -> Dict[str, Any]:
        """
        Retrieves the user's friends leaderboard showing step counts for the last 7 days.

        Args:
            user_id: The encoded ID of the user. Use "-" (dash) for current logged-in user.

        Returns:
            A dictionary containing leaderboard data with:
            - data: List of ranked users including:
                - type: User type ('ranked-user' or 'inactive-user')
                - id: Fitbit user id
                - attributes:
                    - step-rank: Ranking among friends
                    - step-summary: Weekly step count
            - included: List of person details including:
                - avatar: Profile picture URL
                - child: Boolean for child account status
                - friend: Boolean (always true)
                - name: Display name

        Note:
            - Includes data for the previous 6 days plus current day in real time
            - Authorized user (self) is included in the response
            - The 'Average Daily Step Count' privacy setting affects leaderboard inclusion
            - Both active (ranked-user) and inactive (inactive-user) friends are included
        """
        return self._make_request(
            "leaderboard/friends.json", user_id=user_id, api_version=FriendsResource.API_VERSION
        )
