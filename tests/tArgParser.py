import unittest
from ArgParser import ArgParser
from MainConfig import MainConfig
from example.global_vars import default_data_setting_dict


class TestMainArgs(unittest.TestCase):
    """
    These tests depend on the project setting. Changing the project configs setting might break these tests.
    """
    def test_arg_parser_workflow(self):
        mainconf = MainConfig()
        # some creation tests
        actual = mainconf.get_num_args()
        expected = 5
        self.assertEqual(actual, expected)
        actual = mainconf.get_num_configs()
        expected = 0
        self.assertEqual(actual, expected)
        actual = mainconf.get_num_argsgroup()
        expected = 3
        self.assertEqual(actual, expected)
        # now we test parsing
        parser = ArgParser(mainconf)
        parse_str = "--wandb --seed 12123 --dataset sst2"
        parser.parse_args_recursively(parse_str)
        # test the parsed configs
        # test parsed successful
        actual = mainconf.get_num_args()
        expected = 0
        self.assertEqual(actual, expected)
        actual = mainconf.get_num_configs()
        expected = 5
        self.assertEqual(actual, expected)
        actual = mainconf.get_num_argsgroup()
        expected = 3
        self.assertEqual(actual, expected)
        # test user set stuff
        self.assertTrue(mainconf.wandb)
        self.assertEqual(mainconf.seed, 12123)
        self.assertEqual(mainconf.dataset_config.dataset, 'sst2')
        # test dynamic defaults and defaults
        self.assertEqual(mainconf.trainer_config.logger_config.log_dir, 'AUTO')
        self.assertEqual(mainconf.model_config.model, 'bert')
        # test user set stuffs haven't changed
        self.assertTrue(mainconf.wandb)
        self.assertEqual(mainconf.seed, 12123)
        self.assertEqual(mainconf.dataset_config.dataset, 'sst2')
        # test defaults haven't changed
        self.assertEqual(mainconf.trainer_config.logger_config.log_dir, 'AUTO')
        # test defaults have changed according to dataset
        config = default_data_setting_dict['sst2']
        self.assertEqual(mainconf.model_config.model, config['model'])
        self.assertEqual(mainconf.trainer_config.optimizer_config.lr, config['lr'])
        self.assertEqual(mainconf.trainer_config.optimizer_config.weight_decay, config['weight_decay'])
        self.assertEqual(mainconf.trainer_config.optimizer_config.optimizer, config['optimizer'])
        self.assertEqual(mainconf.trainer_config.scheduler_config.scheduler, 'linear')
        self.assertFalse(mainconf.trainer_config.epoch_runner_config.turn_on_torch_amp_autocast)

    def test_dynamic_defaults(self):
        args = MainConfig()
        parser = ArgParser(args)
        parser.parse_args_recursively("--wandb --seed 12123 --dataset wikitext")
        # then set defaults according to global_vars default data dicts
        self.assertEqual(args.trainer_config.scheduler_config.scheduler, 'one_cycle')
        self.assertTrue(args.trainer_config.epoch_runner_config.turn_on_torch_amp_autocast)

    def test_user_override_dynamic_defaults(self):
        args = MainConfig()
        parser = ArgParser(args)
        parser.parse_args_recursively("--wandb --seed 12123 --dataset sst2 --turn_on_torch_amp_autocast")
        # then set defaults according to global_vars default data dicts
        self.assertTrue(args.trainer_config.epoch_runner_config.turn_on_torch_amp_autocast)

    def test_spawn_children(self):
        args = MainConfig()
        parser = ArgParser(args)
        parser.parse_args_recursively("--wandb --seed 12123 --dataset sst2 --scheduler one_cycle")
        # then set defaults according to global_vars default data dicts
        from example.SchedulerConfig import OneCycleLRConfig
        self.assertIsInstance(args.trainer_config.scheduler_config.one_cycle, OneCycleLRConfig)
        self.assertEqual(args.trainer_config.scheduler_config.one_cycle.pct_start, 0.3)

    def test_spawn_children_with_dynamic_defaults(self):
        # spawn children with defaults
        args = MainConfig()
        parser = ArgParser(args)
        parser.parse_args_recursively("--wandb --seed 12123 --dataset wikitext")
        from example.SchedulerConfig import OneCycleLRConfig
        self.assertIsInstance(args.trainer_config.scheduler_config.one_cycle, OneCycleLRConfig)
        self.assertEqual(args.trainer_config.scheduler_config.one_cycle.pct_start, 0.02)
        self.assertEqual(args.model_config.model, 'gptbase')
        self.assertEqual(args.model_config.gpt_base_configs.sequence_length, 4096)
        self.assertEqual(args.model_config.gpt_base_configs.n_layer, 12)

    def test_spawn_children_with_override_dynamic_defaults(self):
        args = MainConfig()
        parser = ArgParser(args)
        parser.parse_args_recursively("--dataset wikitext --n_layer 1234")
        from example.SchedulerConfig import OneCycleLRConfig
        self.assertIsInstance(args.trainer_config.scheduler_config.one_cycle, OneCycleLRConfig)
        self.assertEqual(args.trainer_config.scheduler_config.scheduler_step_every, "batch")
        self.assertEqual(args.trainer_config.scheduler_config.one_cycle.pct_start, 0.02)
        self.assertEqual(args.model_config.model, 'gptbase')
        self.assertEqual(args.model_config.gpt_base_configs.sequence_length, 4096)
        self.assertEqual(args.model_config.gpt_base_configs.n_layer, 1234)

    def test_constraints(self):
        args = MainConfig()
        parser = ArgParser(args)
        parser.parse_args_recursively("--log_every 1 --dataset wikitext")
        self.assertEqual(args.trainer_config.logger_config.log_every, 1)
        args = MainConfig()
        parser = ArgParser(args)
        with self.assertRaises(ValueError):
            # cannot parse negative value to log_every
            parser.parse_args_recursively("--log_every -1 --dataset wikitext")

    def test_dynamic_default_2_levels(self):
        args = MainConfig()
        parser = ArgParser(args)
        parser.parse_args_recursively("--dataset wikitext --scheduler reduce_lr_on_plateau")
        self.assertEqual(args.trainer_config.scheduler_config.scheduler, "reduce_lr_on_plateau")
        self.assertEqual(args.trainer_config.scheduler_config.scheduler_step_every, "epoch")


if __name__ == "__main__":
    unittest.main()
