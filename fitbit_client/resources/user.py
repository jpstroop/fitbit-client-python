# resources/user.py
# Standard library imports
from typing import Any
from typing import Dict
from typing import Optional

# Local imports
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import ClockTimeFormat
from fitbit_client.resources.constants import Gender
from fitbit_client.resources.constants import StartDayOfWeek


class UserResource(BaseResource):
    """
    Handles Fitbit User API endpoints for managing user profile information,
    regional/language settings, and achievement badges.

    Scope: profile

    API Reference: https://dev.fitbit.com/build/reference/web-api/user/
    """

    def get_profile(self, user_id: str = "-") -> Dict[str, Any]:
        """
        Get user profile information.

        Args:
            user_id: Optional user ID, defaults to current user

        Returns:
            User profile data including personal info, preferences, and settings.
            Access to other users' data is subject to their privacy settings.

        Note:
            Numerical values are returned in units specified by Accept-Language header.
            The profile includes all badges visible in the user's badge locker.
        """
        return self._make_request("profile.json", user_id=user_id)

    def update_profile(
        self,
        gender: Optional[Gender] = None,
        birthday: Optional[str] = None,
        height: Optional[str] = None,
        about_me: Optional[str] = None,
        full_name: Optional[str] = None,
        country: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        clock_time_display_format: Optional[ClockTimeFormat] = None,
        start_day_of_week: Optional[StartDayOfWeek] = None,
        locale: Optional[str] = None,
        locale_lang: Optional[str] = None,
        locale_country: Optional[str] = None,
        timezone: Optional[str] = None,
        foods_locale: Optional[str] = None,
        glucose_unit: Optional[str] = None,
        height_unit: Optional[str] = None,
        water_unit: Optional[str] = None,
        weight_unit: Optional[str] = None,
        stride_length_walking: Optional[str] = None,
        stride_length_running: Optional[str] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Update user profile data.

        Args:
            gender: User's gender identity (MALE/FEMALE/NA)
            birthday: Date of birth in YYYY-MM-DD format
            height: Height in X.XX format (units based on Accept-Language)
            about_me: Text for "About Me" profile field
            full_name: User's full name
            country: Two-character country code (requires location scope)
            state: Two-character state code, valid only for US (requires location scope)
            city: City name (requires location scope)
            clock_time_display_format: 12 or 24 hour format
            start_day_of_week: Whether week starts on Sunday or Monday
            locale: Website locale (e.g., en_US, fr_FR)
            locale_lang: Language code (xx format, used if locale not specified)
            locale_country: Country code (xx format, used if locale not specified)
            timezone: Timezone (e.g., "America/Los_Angeles")
            foods_locale: Food database locale (requires nutrition scope)
            glucose_unit: Glucose unit preference (en_US or METRIC)
            height_unit: Height unit preference (en_US or METRIC)
            water_unit: Water unit preference (requires nutrition scope)
            weight_unit: Weight unit preference
            stride_length_walking: Walking stride length in X.XX format
            stride_length_running: Running stride length in X.XX format
            user_id: Optional user ID, defaults to current user

        Returns:
            Updated user profile data

        Note:
            All parameters are optional. Only specified fields will be updated.
            Units for numerical values should match Accept-Language header.
        """
        updates = {
            "gender": gender.value if gender is not None else None,
            "birthday": birthday,
            "height": height,
            "aboutMe": about_me,
            "fullName": full_name,
            "country": country,
            "state": state,
            "city": city,
            "clockTimeDisplayFormat": (
                clock_time_display_format.value if clock_time_display_format is not None else None
            ),
            "startDayOfWeek": start_day_of_week.value if start_day_of_week is not None else None,
            "locale": locale,
            "localeLang": locale_lang,
            "localeCountry": locale_country,
            "timezone": timezone,
            "foodsLocale": foods_locale,
            "glucoseUnit": glucose_unit,
            "heightUnit": height_unit,
            "waterUnit": water_unit,
            "weightUnit": weight_unit,
            "strideLengthWalking": stride_length_walking,
            "strideLengthRunning": stride_length_running,
        }

        params = {key: value for key, value in updates.items() if value is not None}
        return self._post("profile.json", params=params, user_id=user_id)

    def get_badges(self, user_id: str = "-") -> Dict[str, Any]:
        """
        Get list of user's earned achievement badges.

        Args:
            user_id: Optional user ID, defaults to current user

        Returns:
            List of badges earned by the user

        Note:
            Access to badges requires user's "My Achievements" privacy setting
            to allow access. Weight badges are only included if "My Body" privacy
            setting allows access.
        """
        return self._make_request("badges.json", user_id=user_id)
