# tests/resources/test_docstrings.py

# Standard library imports
from inspect import getdoc
from inspect import getmembers
from inspect import isclass
from inspect import isfunction
from re import search
from typing import List
from typing import Type

# Third party imports
from pytest import fail
from pytest import mark

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


def get_all_resource_classes() -> List[Type]:
    """Return all resource classes for testing"""
    return [
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


def test_class_docstring_has_api_reference():
    """Test that every resource class docstring includes API Reference URL"""
    failures = []

    for resource_cls in get_all_resource_classes():
        docstring = getdoc(resource_cls)
        api_ref_pattern = r"API Reference: https://dev\.fitbit\.com/build/reference/web-api/.+"

        if not docstring or not search(api_ref_pattern, docstring):
            failures.append(f"{resource_cls.__name__}")

    if failures:
        fail_msg = "The following resource classes are missing API Reference URLs in their class docstrings:\n"
        fail_msg += "\n".join(failures)
        fail(fail_msg)


def test_class_docstring_has_required_scopes():
    """Test that every resource class docstring includes Required Scopes section"""
    failures = []

    for resource_cls in get_all_resource_classes():
        docstring = getdoc(resource_cls)
        required_scopes_pattern = r"Required Scopes:"

        if not docstring or not search(required_scopes_pattern, docstring):
            failures.append(f"{resource_cls.__name__}")

    if failures:
        fail_msg = "The following resource classes are missing Required Scopes section in their class docstrings:\n"
        fail_msg += "\n".join(failures)
        fail(fail_msg)


@mark.parametrize("section_name", ["Args:", "Returns:", "Raises:", "API Reference:", "Note:"])
def test_method_docstring_has_required_section(section_name):
    """Test that every public method in resource modules has the required docstring sections"""
    failures = []

    for resource_cls in get_all_resource_classes():
        methods = get_public_methods(resource_cls)

        for method_name in methods:
            method = getattr(resource_cls, method_name)

            # Skip aliased methods that share docstrings
            if method.__doc__ is None:
                continue

            docstring = getdoc(method)

            # Allow NotImplemented methods to skip sections
            if docstring and "NOT IMPLEMENTED" in docstring:
                continue

            # Check for the specified section
            if not docstring or not search(rf"{section_name}", docstring):
                failures.append(f"{resource_cls.__name__}.{method_name} missing {section_name}")

    if failures:
        fail_msg = (
            f"The following methods are missing the {section_name} section in their docstrings:\n"
        )
        fail_msg += "\n".join(failures)
        fail(fail_msg)


def test_api_reference_in_method_docstrings():
    """Test that every public method in resource modules has an API Reference URL"""
    failures = []

    for resource_cls in get_all_resource_classes():
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


def test_docstring_sections_order():
    """Test that docstring sections appear in the correct order when present"""
    expected_order = ["Args:", "Returns:", "Raises:", "Note:"]
    failures = []

    for resource_cls in get_all_resource_classes():
        methods = get_public_methods(resource_cls)

        for method_name in methods:
            method = getattr(resource_cls, method_name)

            # Skip aliased methods that share docstrings
            if method.__doc__ is None:
                continue

            docstring = getdoc(method)

            # Allow NotImplemented methods to skip checks
            if docstring and "NOT IMPLEMENTED" in docstring:
                continue

            # Find positions of each section in the docstring
            positions = {}
            for section in expected_order:
                match = search(rf"{section}", docstring)
                if match:
                    positions[section] = match.start()

            # Check if found sections are in the correct order
            sections_found = sorted(positions.keys(), key=lambda k: positions[k])
            expected_sections = [s for s in expected_order if s in positions]

            if sections_found != expected_sections:
                failures.append(
                    f"{resource_cls.__name__}.{method_name} has incorrect section order: "
                    f"found {sections_found}, expected {expected_sections}"
                )

    if failures:
        fail_msg = "The following methods have docstring sections in the wrong order:\n"
        fail_msg += "\n".join(failures)
        fail(fail_msg)
