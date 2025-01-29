# tests/client/test_resource_aliases.py

"""
Test that all resource methods are properly aliased in ClientMethodsMixin.
"""

# Standard library imports
from inspect import getmembers
from inspect import ismethod
from inspect import signature
from typing import Dict
from typing import Type

# Local imports
from fitbit_client.client.resource_methods_mixin import ClientMethodsMixin
from fitbit_client.resources.activezone import ActiveZoneResource
from fitbit_client.resources.activity import ActivityResource
from fitbit_client.resources.activity_timeseries import ActivityTimeSeriesResource
from fitbit_client.resources.body import BodyResource
from fitbit_client.resources.body_timeseries import BodyTimeSeriesResource
from fitbit_client.resources.breathingrate import BreathingRateResource
from fitbit_client.resources.cardio_fitness import CardioFitnessResource
from fitbit_client.resources.device import DeviceResource
from fitbit_client.resources.ecg import ECGResource
from fitbit_client.resources.friends import FriendsResource
from fitbit_client.resources.heartrate_timeseries import HeartRateTimeSeriesResource
from fitbit_client.resources.heartrate_variability import HeartRateVariabilityResource
from fitbit_client.resources.irregular_rhythm import IrregularRhythmResource
from fitbit_client.resources.nutrition import NutritionResource
from fitbit_client.resources.nutrition_timeseries import NutritionTimeSeriesResource
from fitbit_client.resources.sleep import SleepResource
from fitbit_client.resources.spo2 import SpO2Resource
from fitbit_client.resources.subscription import SubscriptionResource
from fitbit_client.resources.temperature import TemperatureResource
from fitbit_client.resources.user import UserResource

# All resource classes that should have their methods aliased
RESOURCE_CLASSES = [
    ActiveZoneResource,
    ActivityResource,
    ActivityTimeSeriesResource,
    BodyResource,
    BodyTimeSeriesResource,
    BreathingRateResource,
    CardioFitnessResource,
    DeviceResource,
    ECGResource,
    FriendsResource,
    HeartRateTimeSeriesResource,
    HeartRateVariabilityResource,
    IrregularRhythmResource,
    NutritionResource,
    NutritionTimeSeriesResource,
    SleepResource,
    SpO2Resource,
    SubscriptionResource,
    TemperatureResource,
    UserResource,
]

# Methods that were renamed to avoid naming conflicts
METHOD_RENAMES = {
    # Original method name -> New alias name(s)
    "get_time_series": ["get_activity_time_series"],
    "get_time_series_by_date_range": ["get_activity_time_series_by_date_range"],
    "get_time_series_by_date": [
        "get_body_time_series_by_date",
        "get_heartrate_by_date",
        "get_nutrition_time_series_by_date",
    ],
}


def get_public_methods(cls: Type) -> Dict[str, signature]:
    """Get all public methods and their signatures from a class."""
    return {
        name: signature(method)
        for name, method in getmembers(cls, ismethod)
        if not name.startswith("_")
    }


def check_method_signatures(
    original_name: str, original_sig: signature, alias_name: str, alias_sig: signature
) -> str:
    """Compare method signatures and return error message if they don't match."""
    if original_sig != alias_sig:
        return f"Signature mismatch: {original_name}{original_sig} != " f"{alias_name}{alias_sig}"
    return ""


def test_all_resource_methods_have_aliases():
    """Verify all resource methods have corresponding aliases with matching signatures."""
    mixin_methods = get_public_methods(ClientMethodsMixin)
    errors = []

    for resource_class in RESOURCE_CLASSES:
        resource_methods = get_public_methods(resource_class)

        for method_name, resource_sig in resource_methods.items():
            # Check if method was renamed
            if method_name in METHOD_RENAMES:
                # Check all possible rename variants
                found_alias = False
                for alias_name in METHOD_RENAMES[method_name]:
                    if alias_name in mixin_methods:
                        found_alias = True
                        error = check_method_signatures(
                            f"{resource_class.__name__}.{method_name}",
                            resource_sig,
                            f"ClientMethodsMixin.{alias_name}",
                            mixin_methods[alias_name],
                        )
                        if error:
                            errors.append(error)
                if not found_alias:
                    errors.append(
                        f"Missing alias for renamed method: {resource_class.__name__}.{method_name}"
                    )

            # Check for direct alias
            elif method_name not in mixin_methods:
                errors.append(f"Missing alias: {resource_class.__name__}.{method_name}")
            else:
                error = check_method_signatures(
                    f"{resource_class.__name__}.{method_name}",
                    resource_sig,
                    f"ClientMethodsMixin.{method_name}",
                    mixin_methods[method_name],
                )
                if error:
                    errors.append(error)

    assert not errors, "\n".join(errors)
