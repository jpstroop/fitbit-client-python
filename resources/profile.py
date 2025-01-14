# resources/profile.py
from resources.base import BaseResource
from typing import Any
from typing import Dict


class ProfileResource(BaseResource):
    """
    Handles Fitbit Profile API endpoints
    API Reference: https://dev.fitbit.com/build/reference/web-api/user/
    """

    def get_profile(self, user_id: str = "-") -> Dict[str, Any]:
        """
        Get user profile information.

        Returns full user profile including name, badges, settings, and more.
        """
        return self._get("profile.json", user_id=user_id)

    def update_profile(self, data: Dict[str, Any], user_id: str = "-") -> Dict[str, Any]:
        """
        Update profile information for a user.

        Parameters:
            data: Dictionary of fields to update. Valid fields include:
                - gender
                - birthday
                - height
                - weight
                - aboutMe
                - country
                - state
                - city
                - timezone
        """
        return self._post("profile.json", json=data, user_id=user_id)

    def get_badges(self, user_id: str = "-") -> Dict[str, Any]:
        """Get list of user's badges."""
        return self._get("badges.json", user_id=user_id)
