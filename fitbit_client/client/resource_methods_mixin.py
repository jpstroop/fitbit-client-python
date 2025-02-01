# fitbit_client/client/resource_methods_mixin.py

# Standard library imports
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

# Local imports
from fitbit_client.resources.constants import ActivityGoalType
from fitbit_client.resources.constants import BodyGoalType
from fitbit_client.resources.constants import BodyResourceType
from fitbit_client.resources.constants import BodyTimePeriod
from fitbit_client.resources.constants import ClockTimeFormat
from fitbit_client.resources.constants import FoodFormType
from fitbit_client.resources.constants import FoodPlanIntensity
from fitbit_client.resources.constants import Gender
from fitbit_client.resources.constants import MealType
from fitbit_client.resources.constants import NutritionResource as NutritionResourceType
from fitbit_client.resources.constants import Period
from fitbit_client.resources.constants import SleepType
from fitbit_client.resources.constants import StartDayOfWeek
from fitbit_client.resources.constants import SubscriptionCategory
from fitbit_client.resources.constants import WaterUnit
from fitbit_client.resources.constants import WeekDay


class ClientMethodsMixin:
    """
    Mixin class that provides direct access to resource methods on the client.

    The following methods have been renamed from their original resource
    implementations to avoid naming collisions when exposed directly on the
    client:

    Activity Time Series
     - `get_time_series()` → `get_activity_time_series()`
     - `get_time_series_by_date_range()` → `get_activity_time_series_by_date_range()`

    Body Time Series
     - `get_time_series_by_date()` → `get_body_time_series_by_date()`

    Heart Rate Time Series
     - `get_time_series_by_date()` → `get_heartrate_by_date()`
     - `get_time_series_by_date_range()` → `get_heartrate_by_date_range()`

    Nutrition Time Series
     - `get_time_series_by_date()` → `get_nutrition_time_series_by_date()`
     - `get_time_series_by_date_range()` → `get_nutrition_time_series_by_date_range()`

    All other methods maintain their original names from their respective
    resource classes.
    """

    pass
    # This will be re-implemented after resource methods have been refactored.
