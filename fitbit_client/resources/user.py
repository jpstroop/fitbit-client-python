# fitbit_client/resources/user.py

# Standard library imports
from typing import Optional
from typing import cast

# Local imports
from fitbit_client.resources._base import BaseResource
from fitbit_client.resources._constants import ClockTimeFormat
from fitbit_client.resources._constants import Gender
from fitbit_client.resources._constants import StartDayOfWeek
from fitbit_client.utils.date_validation import validate_date_param
from fitbit_client.utils.types import JSONDict
from fitbit_client.utils.types import ParamDict


class UserResource(BaseResource):
    """Provides access to Fitbit User API for managing profile and badge information.

    This resource handles endpoints for retrieving and updating user profile information,
    including personal details, regional/language settings, measurement preferences, and
    achievement badges. It allows applications to personalize user experiences and display
    user accomplishments.

    API Reference: https://dev.fitbit.com/build/reference/web-api/user/

    Required Scopes:
      - profile: Required for basic profile information access and updates
      - location: Required for accessing and updating regional settings (country, state, city)
      - nutrition: Required for updating food preferences (foods locale, water units)

    Note:
        The User API contains core user information that affects how data is displayed across
        the entire Fitbit platform. Settings such as measurement units, locale preferences,
        and timezone determine how data is formatted in all other API responses.

        Access to other users' profile information is subject to their privacy settings,
        particularly the "Personal Info" privacy setting, which must be set to either
        "Friends" or "Public" to allow access.

        While the profile endpoint requires minimal scope, updating some profile fields
        (like location and food preferences) requires additional scopes.
    """

    def get_profile(self, user_id: str = "-", debug: bool = False) -> JSONDict:
        """Returns a user's profile information.

        This endpoint retrieves detailed information about a user's profile, including
        personal details, preferences, and settings. This data can be used to personalize
        the application experience and ensure correct data formatting.

        API Reference: https://dev.fitbit.com/build/reference/web-api/user/get-profile/

        Args:
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: User profile data containing personal information (name, gender, birth date),
                  activity metrics (height, weight, stride length), and preferences (units,
                  timezone, locale settings)

        Raises:
            fitbit_client.exceptions.AuthorizationException: If required scope is not granted
            fitbit_client.exceptions.ForbiddenException: If privacy settings restrict access

        Note:
            Numerical values (height, weight) are returned in units specified by
            the Accept-Language header provided during client initialization.

            Access to other users' profile data is subject to their privacy settings.
            The "Personal Info" privacy setting must be set to either "Friends" or
            "Public" to allow access to other users' profiles.

            Some fields may be missing if they haven't been set by the user or if
            privacy settings restrict access to them.
        """
        result = self._make_request("profile.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)

    @validate_date_param(field_name="birthday")
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
        debug: bool = False,
    ) -> JSONDict:
        """
        Updates the user's profile information.

        API Reference: https://dev.fitbit.com/build/reference/web-api/user/update-profile/

        Args:
            gender: User's gender identity (Gender.MALE, Gender.FEMALE, or Gender.NA)
            birthday: Date of birth in YYYY-MM-DD format
            height: Height in X.XX format (units based on Accept-Language header)
            about_me: Text for "About Me" profile field
            full_name: User's full name
            country: Two-character country code (requires location scope)
            state: Two-character state code, valid only for US (requires location scope)
            city: City name (requires location scope)
            clock_time_display_format: 12 or 24 hour format (ClockTimeFormat.TWELVE_HOUR
                                       or ClockTimeFormat.TWENTY_FOUR_HOUR)
            start_day_of_week: First day of week (StartDayOfWeek.SUNDAY or StartDayOfWeek.MONDAY)
            locale: Website locale (e.g., "en_US", "fr_FR")
            locale_lang: Language code (e.g., "en", used if locale not specified)
            locale_country: Country code (e.g., "US", used if locale not specified)
            timezone: Timezone (e.g., "America/Los_Angeles")
            foods_locale: Food database locale (e.g., "en_US", requires nutrition scope)
            glucose_unit: Glucose unit preference ("en_US" or "METRIC")
            height_unit: Height unit preference ("en_US" or "METRIC")
            water_unit: Water unit preference (requires nutrition scope)
            weight_unit: Weight unit preference ("en_US" or "METRIC")
            stride_length_walking: Walking stride length in X.XX format
            stride_length_running: Running stride length in X.XX format
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Updated user profile data with the same structure as get_profile()

        Raises:
            fitbit_client.exceptions.InvalidDateException: If birthday format is invalid

        Note:
            All parameters are optional. Only specified fields will be updated.
            Units for numerical values should match the Accept-Language header.
            Updating location information (country, state, city) requires the 'location' scope.
            Updating food preferences requires the 'nutrition' scope.
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

        # Create a ParamDict from the non-None values
        params: ParamDict = {key: value for key, value in updates.items() if value is not None}
        result = self._make_request(
            "profile.json", params=params, user_id=user_id, http_method="POST", debug=debug
        )
        return cast(JSONDict, result)

    def get_badges(self, user_id: str = "-", debug: bool = False) -> JSONDict:
        """
        Returns a list of the user's earned achievement badges.

        API Reference: https://dev.fitbit.com/build/reference/web-api/user/get-badges/

        Args:
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Contains categorized lists of badges earned by the user (all badges, daily goal badges,
                  lifetime achievement badges, and weight goal badges), with detailed information about
                  each badge including description, achievement date, and visual elements

        Raises:
            fitbit_client.exceptions.AuthorizationException: If required profile scope is not granted
            fitbit_client.exceptions.ForbiddenException: If privacy settings restrict access

        Note:
            Access to badges requires user's "My Achievements" privacy setting
            to allow access. Weight badges are only included if "My Body" privacy
            setting allows access. Some fields may not be present for all badges.
        """
        result = self._make_request("badges.json", user_id=user_id, debug=debug)
        return cast(JSONDict, result)
