# tests/resources/test_docstrings.py

# Standard library imports
from inspect import getdoc
from inspect import getmembers
from inspect import isfunction
from re import search
from typing import List

# Third party imports
from pytest import fail

# fmt: off
# isort: off
from fitbit_client.resources.active_zone_minutes import ActiveZoneMinutesResource
from fitbit_client.resources.activity import ActivityResource
from fitbit_client.resources.activity_timeseries import ActivityTimeSeriesResource
from fitbit_client.resources.body import BodyResource
from fitbit_client.resources.body_timeseries import BodyTimeSeriesResource
from fitbit_client.resources.breathing_rate import BreathingRateResource
from fitbit_client.resources.cardio_fitness_score import CardioFitnessScoreResource
from fitbit_client.resources.device import DeviceResource
from fitbit_client.resources.electrocardiogram import ElectrocardiogramResource
from fitbit_client.resources.friends import FriendsResource
from fitbit_client.resources.heartrate_timeseries import HeartrateTimeSeriesResource
from fitbit_client.resources.heartrate_variability import HeartrateVariabilityResource
from fitbit_client.resources.intraday import IntradayResource
from fitbit_client.resources.irregular_rhythm_notifications import IrregularRhythmNotificationsResource
from fitbit_client.resources.nutrition import NutritionResource
from fitbit_client.resources.nutrition_timeseries import NutritionTimeSeriesResource
from fitbit_client.resources.sleep import SleepResource
from fitbit_client.resources.spo2 import SpO2Resource
from fitbit_client.resources.subscription import SubscriptionResource
from fitbit_client.resources.temperature import TemperatureResource
from fitbit_client.resources.user import UserResource
# isort: on
# fmt: on


def get_public_methods(cls) -> List[str]:
    """Get all public methods from a class (excluding dunder methods)"""
    return [
        name for name, member in getmembers(cls, predicate=isfunction) if not name.startswith("_")
    ]


def test_api_reference_in_docstrings():
    """Test that every public method in resource modules has an API Reference URL"""

    # Get all resource modules
    resources = [
        ActiveZoneMinutesResource,
        ActivityResource,
        ActivityTimeSeriesResource,
        BodyResource,
        BodyTimeSeriesResource,
        BreathingRateResource,
        CardioFitnessScoreResource,
        DeviceResource,
        ElectrocardiogramResource,
        FriendsResource,
        HeartrateTimeSeriesResource,
        HeartrateVariabilityResource,
        IntradayResource,
        IrregularRhythmNotificationsResource,
        NutritionResource,
        NutritionTimeSeriesResource,
        SleepResource,
        SpO2Resource,
        SubscriptionResource,
        TemperatureResource,
        UserResource,
    ]

    failures = []

    # Check each resource class
    for resource_cls in resources:
        methods = get_public_methods(resource_cls)

        for method_name in methods:
            method = getattr(resource_cls, method_name)

            # Skip aliased methods that share docstrings
            if method.__doc__ is None:
                continue

            docstring = getdoc(method)

            # Allow NotImplemented methods to skip API reference
            if docstring and "NOT IMPLEMENTED" in docstring:
                continue

            api_ref_pattern = r"API Reference: https://dev\.fitbit\.com/build/reference/web-api/.+"

            if not docstring or not search(api_ref_pattern, docstring):
                failures.append(f"{resource_cls.__name__}.{method_name}")

    if failures:
        fail_msg = "The following methods are missing API Reference URLs in their docstrings:\n"
        fail_msg += "\n".join(failures)
        fail(fail_msg)
