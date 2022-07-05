"""Verifies the Supported_settings object catches invalid min_max_graphs
specifications."""
# pylint: disable=R0801
import copy
import unittest

from src.experiment_settings.Supported_settings import Supported_settings
from src.experiment_settings.verify_supported_settings import (
    verify_configuration_settings,
)
from tests.experiment_settings.test_generic_configuration import (
    adap_sets,
    rad_sets,
    supp_sets,
    verify_error_is_thrown_on_invalid_configuration_setting_value,
    with_adaptation_with_radiation,
)


class Test_min_max_graphs_settings(unittest.TestCase):
    """Tests whether the verify_configuration_settings_types function catches
    invalid min_max_graphs settings.."""

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.supp_sets = Supported_settings()
        self.valid_min_max_graphs = self.supp_sets.min_max_graphs

        self.invalid_min_max_graphs_value = {
            "min_max_graphs": "invalid value of type string iso list of"
            + " floats",
        }

        self.supp_sets = supp_sets
        self.adap_sets = adap_sets
        self.rad_sets = rad_sets
        self.with_adaptation_with_radiation = with_adaptation_with_radiation

    def test_error_is_thrown_if_min_max_graphs_key_is_missing(self):
        """Verifies an exception is thrown if an empty min_max_graphs dict is
        thrown."""

        # Create deepcopy of configuration settings.
        config_settings = copy.deepcopy(self.with_adaptation_with_radiation)
        # Remove key and value of m.

        config_settings.pop("min_max_graphs")

        with self.assertRaises(Exception) as context:
            verify_configuration_settings(
                self.supp_sets, config_settings, has_unique_id=False
            )

        self.assertEqual(
            # "'min_max_graphs'",
            "Error:min_max_graphs is not in the configuration"
            + f" settings:{config_settings.keys()}",
            str(context.exception),
        )

    def test_error_is_thrown_for_invalid_min_max_graphs_value_type(self):
        """Verifies an exception is thrown if the configuration setting:

        min_max_graphs is of invalid type.
        """

        # Create deepcopy of configuration settings.
        config_settings = copy.deepcopy(self.with_adaptation_with_radiation)
        expected_type = type(self.supp_sets.min_max_graphs)

        # Verify it throws an error on None and string.
        for invalid_config_setting_value in [None, ""]:
            config_settings["min_max_graphs"] = invalid_config_setting_value
            verify_error_is_thrown_on_invalid_configuration_setting_value(
                invalid_config_setting_value,
                config_settings,
                expected_type,
                self,
            )

    # TODO: test_catch_empty_min_max_graphs_value_list

    def test_catch_min_max_graphs_value_too_low(self):
        """."""
        # Create deepcopy of configuration settings.
        config_settings = copy.deepcopy(self.with_adaptation_with_radiation)
        # Set negative value of min_max_graphs in copy.
        config_settings["min_max_graphs"] = -2

        with self.assertRaises(Exception) as context:
            verify_configuration_settings(
                self.supp_sets, config_settings, has_unique_id=False
            )

        self.assertEqual(
            "Error, setting expected to be at least "
            + f"{self.supp_sets.min_max_graphs}. "
            + f"Instead, it is:{-2}",
            str(context.exception),
        )

    def test_catch_min_max_graphs_value_too_high(self):
        """."""
        # Create deepcopy of configuration settings.
        config_settings = copy.deepcopy(self.with_adaptation_with_radiation)
        # Set negative value of min_max_graphs in copy.
        config_settings["min_max_graphs"] = 50

        with self.assertRaises(Exception) as context:
            verify_configuration_settings(
                self.supp_sets, config_settings, has_unique_id=False
            )

        self.assertEqual(
            "Error, setting expected to be at most "
            + f"{self.supp_sets.max_max_graphs}. Instead, it is:"
            + "50",
            str(context.exception),
        )
