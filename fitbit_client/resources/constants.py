# fitbit_client/resources/constants.py

# Standard library imports
from enum import Enum


class Period(str, Enum):
    """
    Time periods for Fitbit API endpoints.

    Different resources may support different subsets of these periods.
    Check individual resource documentation for supported values.
    """

    ONE_DAY = "1d"  # One day
    SEVEN_DAYS = "7d"  # Seven days
    THIRTY_DAYS = "30d"  # Thirty days
    ONE_WEEK = "1w"  # One week
    ONE_MONTH = "1m"  # One month
    THREE_MONTHS = "3m"  # Three months
    SIX_MONTHS = "6m"  # Six months
    ONE_YEAR = "1y"  # One year
    MAX = "max"  # Maximum available data


class ActivityGoalType(str, Enum):
    """Activity goal types supported by Fitbit"""

    ACTIVE_MINUTES = "activeMinutes"
    ACTIVE_ZONE_MINUTES = "activeZoneMinutes"
    CALORIES_OUT = "caloriesOut"
    DISTANCE = "distance"
    FLOORS = "floors"
    STEPS = "steps"


class MaxRanges(int, Enum):
    """Maximum date ranges for various resources (in days)"""

    BREATHING_RATE = 30
    BODY_FAT = 30
    WEIGHT = 31
    ACTIVITY = 31
    SLEEP = 100
    GENERAL = 1095
    INTRADAY = 1


class ActivityTimeSeriesPath(str, Enum):
    """Resource paths available for activity time series data

    API Reference: https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity-timeseries-by-date/#Resource-Options
    """

    ACTIVITY_CALORIES = "activityCalories"
    CALORIES = "calories"
    CALORIES_BMR = "caloriesBMR"
    DISTANCE = "distance"
    ELEVATION = "elevation"
    FLOORS = "floors"
    MINUTES_SEDENTARY = "minutesSedentary"
    MINUTES_LIGHTLY_ACTIVE = "minutesLightlyActive"
    MINUTES_FAIRLY_ACTIVE = "minutesFairlyActive"
    MINUTES_VERY_ACTIVE = "minutesVeryActive"
    STEPS = "steps"
    SWIMMING_STROKES = "swimming-strokes"

    # Tracker-only paths
    TRACKER_ACTIVITY_CALORIES = "tracker/activityCalories"
    TRACKER_CALORIES = "tracker/calories"
    TRACKER_DISTANCE = "tracker/distance"
    TRACKER_ELEVATION = "tracker/elevation"
    TRACKER_FLOORS = "tracker/floors"
    TRACKER_MINUTES_SEDENTARY = "tracker/minutesSedentary"
    TRACKER_MINUTES_LIGHTLY_ACTIVE = "tracker/minutesLightlyActive"
    TRACKER_MINUTES_FAIRLY_ACTIVE = "tracker/minutesFairlyActive"
    TRACKER_MINUTES_VERY_ACTIVE = "tracker/minutesVeryActive"
    TRACKER_STEPS = "tracker/steps"


class ActivityGoalPeriod(str, Enum):
    """Periods for the user's specified current activity goals."""

    WEEKLY = "weekly"
    DAILY = "daily"


class GoalType(str, Enum):
    """Goal types for body weight goals."""

    LOSE = "LOSE"
    GAIN = "GAIN"
    MAINTAIN = "MAINTAIN"


class BodyGoalType(str, Enum):
    """Types of body measurement goals supported by the Get Body Goals endpoint."""

    FAT = "fat"
    WEIGHT = "weight"


class BodyTimePeriod(str, Enum):
    """Time periods for body measurement time series endpoints."""

    ONE_DAY = "1d"
    SEVEN_DAYS = "7d"
    THIRTY_DAYS = "30d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1m"
    THREE_MONTHS = "3m"
    SIX_MONTHS = "6m"
    ONE_YEAR = "1y"
    MAX = "max"


class BodyResourceType(str, Enum):
    """Resource types for body measurement time series."""

    BMI = "bmi"
    FAT = "fat"
    WEIGHT = "weight"


class WeekDay(str, Enum):
    """Days of the week for alarm settings."""

    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class MealType(int, Enum):
    """Meal types supported by the Fitbit nutrition API."""

    BREAKFAST = 1
    MORNING_SNACK = 2
    LUNCH = 3
    AFTERNOON_SNACK = 4
    DINNER = 5
    EVENING_SNACK = 6  # this works even though it is not documented
    ANYTIME = 7


class FoodFormType(str, Enum):
    """Food texture types for creating custom foods."""

    LIQUID = "LIQUID"
    DRY = "DRY"


class FoodPlanIntensity(str, Enum):
    """Intensity levels for food plan goals."""

    MAINTENANCE = "MAINTENANCE"
    EASIER = "EASIER"
    MEDIUM = "MEDIUM"
    KINDAHARD = "KINDAHARD"
    HARDER = "HARDER"


class WaterUnit(str, Enum):
    """Valid units for water measurement."""

    MILLILITERS = "ml"
    FLUID_OUNCES = "fl oz"
    CUPS = "cup"


class NutritionalValue(str, Enum):
    """Common nutritional value parameter names for food creation and logging."""

    # Common Nutrients
    CALORIES_FROM_FAT = "caloriesFromFat"
    TOTAL_FAT = "totalFat"
    TRANS_FAT = "transFat"
    SATURATED_FAT = "saturatedFat"
    CHOLESTEROL = "cholesterol"
    SODIUM = "sodium"
    POTASSIUM = "potassium"
    TOTAL_CARBOHYDRATE = "totalCarbohydrate"
    DIETARY_FIBER = "dietaryFiber"
    SUGARS = "sugars"
    PROTEIN = "protein"

    # Vitamins
    VITAMIN_A = "vitaminA"  # IU
    VITAMIN_B6 = "vitaminB6"
    VITAMIN_B12 = "vitaminB12"
    VITAMIN_C = "vitaminC"  # mg
    VITAMIN_D = "vitaminD"  # IU
    VITAMIN_E = "vitaminE"  # IU
    BIOTIN = "biotin"  # mg
    FOLIC_ACID = "folicAcid"  # mg
    NIACIN = "niacin"  # mg
    PANTOTHENIC_ACID = "pantothenicAcid"  # mg
    RIBOFLAVIN = "riboflavin"  # mg
    THIAMIN = "thiamin"  # mg

    # Dietary Minerals
    CALCIUM = "calcium"  # g
    COPPER = "copper"  # g
    IRON = "iron"  # mg
    MAGNESIUM = "magnesium"  # mg
    PHOSPHORUS = "phosphorus"  # g
    IODINE = "iodine"  # mcg
    ZINC = "zinc"  # mg


class NutritionResource(str, Enum):
    """Resources available for nutrition time series data."""

    CALORIES_IN = "caloriesIn"
    WATER = "water"


class SubscriptionCategory(str, Enum):
    """Categories of data available for Fitbit API subscriptions"""

    ACTIVITIES = "activities"  # Requires activity scope
    BODY = "body"  # Requires weight scope
    FOODS = "foods"  # Requires nutrition scope
    SLEEP = "sleep"  # Requires sleep scope
    USER_REVOKED_ACCESS = "userRevokedAccess"  # No scope required


class Gender(str, Enum):
    """Gender options for user profile"""

    MALE = "MALE"
    FEMALE = "FEMALE"
    NA = "NA"


class ClockTimeFormat(str, Enum):
    """Time display format options"""

    TWELVE_HOUR = "12hour"
    TWENTY_FOUR_HOUR = "24hour"


class StartDayOfWeek(str, Enum):
    """Options for first day of week"""

    SUNDAY = "SUNDAY"
    MONDAY = "MONDAY"


class IntradayDetailLevel(str, Enum):
    """Detail levels for intraday data"""

    ONE_SECOND = "1sec"
    ONE_MINUTE = "1min"
    FIVE_MINUTES = "5min"
    FIFTEEN_MINUTES = "15min"
