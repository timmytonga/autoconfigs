"""
Tests for args
"""

from MainConfig import MainConfig
import unittest
from Arg import Arg


class TestMainArgs(unittest.TestCase):

    def test_args_group_get_root(self):
        mainconf = MainConfig()
        dataset_conf = mainconf.dataset_config
        root = dataset_conf.get_root_argsgroup()
        self.assertEqual(mainconf, root)
        epoch_runner_conf = mainconf.trainer_config.epoch_runner_config
        root = epoch_runner_conf.get_root_argsgroup()
        self.assertEqual(mainconf, root)

    def test_argsgroup_children(self):
        from ArgsGroup import pretty_str_list_of_argsgroup
        mainconf = MainConfig()
        result = pretty_str_list_of_argsgroup(mainconf.get_children_argsgroup())
        expected = '[DatasetConfig, ModelConfig, TrainerConfig]'
        self.assertEqual(result, expected)

    def test_argsgroup_arg_iterate(self):
        from dataclasses import fields
        mainconf = MainConfig()
        args = mainconf.get_children_args()
        self.assertEqual(len(args), len(fields(mainconf)))
        children_argsgroup = mainconf.get_all_children_argsgroup()
        for argsgroup in children_argsgroup:
            args = argsgroup.get_children_args()
            arg_fields = list(filter(lambda x: isinstance(getattr(argsgroup, x.name), Arg), fields(argsgroup)))
            self.assertEqual(
                len(args), len(arg_fields),
                f"Failed for: {str(argsgroup)}. #args={len(args)} vs. #fields={len(arg_fields)}")


if __name__ == "__main__":
    unittest.main()
