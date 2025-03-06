# tests/test_method_aliases.py

# Third party imports
import pytest

# Local imports
from fitbit_client.client import FitbitClient


class TestMethodAliases:
    """Test that all resource methods are properly aliased in the client."""

    def test_method_aliases_implementation(self):
        """Verify that the client has set up method aliases for all resources."""
        # Check that the client file has the required method and call
        with open(
            "/Users/jstroop/workspace/fitbit-client-python/fitbit_client/client.py", "r"
        ) as f:
            client_content = f.read()

        # Check that the _setup_method_aliases method exists
        assert (
            "def _setup_method_aliases" in client_content
        ), "The _setup_method_aliases method is missing"

        # Check that it's called in __init__
        assert (
            "self._setup_method_aliases()" in client_content
        ), "_setup_method_aliases() is not called in __init__"

        # Check that there are assignments for all resources
        resources = [
            "active_zone_minutes",
            "activity",
            "activity_timeseries",
            "body",
            "body_timeseries",
            "breathing_rate",
            "cardio_fitness_score",
            "device",
            "electrocardiogram",
            "friends",
            "heartrate_timeseries",
            "heartrate_variability",
            "intraday",
            "irregular_rhythm_notifications",
            "nutrition",
            "nutrition_timeseries",
            "sleep",
            "spo2",
            "subscription",
            "temperature",
            "user",
        ]

        for resource in resources:
            # Check at least one method from each resource is aliased
            assert f"self.{resource}." in client_content, f"No method aliases found for {resource}"
