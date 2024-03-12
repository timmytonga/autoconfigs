from dataclasses import dataclass
from Arg import IntArg, StrArg, BoolArg
from ArgsGroup import ArgsGroup
from example.global_vars import default_data_setting_dict
# configs
from example.LoggingConfig import LoggingConfig
from example.EpochRunnerConfig import EpochRunnerConfig
from example.CheckpointingConfig import CheckpointingConfig
from example.OptimizerConfig import OptimizerConfig
from example.SchedulerConfig import SchedulerConfig


AVAIL_CRITERIONS = ['cross_entropy', 'square']


@dataclass
class TrainerConfig(ArgsGroup):

    def __post_init__(self):
        ArgsGroup.__init__(self, "TrainerConfig", "Trainer Configs for the project")
        self.epoch_runner_config = EpochRunnerConfig()
        self.logger_config = LoggingConfig()
        self.checkpointing_config = CheckpointingConfig()
        self.optimizer_config = OptimizerConfig()
        self.scheduler_config = SchedulerConfig()

    # these are Args and are passed
    n_epochs: int = IntArg(
        "n_epochs", default=100,
        dynamic_defaults_dict=default_data_setting_dict
    )
    loss: str = StrArg(
        "loss", choices=AVAIL_CRITERIONS, default='cross_entropy',
        dynamic_defaults_dict=default_data_setting_dict
    )
    no_test: bool = BoolArg(
        "no_test", action="store_true", help="Do not evaluate on test set", default=False,
        dynamic_defaults_dict=default_data_setting_dict
    )
    no_val: bool = BoolArg(
        "no_val", action="store_true", help="Do not evaluate on val set", default=False,
        dynamic_defaults_dict=default_data_setting_dict
    )
