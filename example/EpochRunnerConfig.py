from dataclasses import dataclass
from Arg import BoolArg, IntArg
from ArgsGroup import ArgsGroup
from example.global_vars import default_data_setting_dict

from example.GradProcessingConfig import GradProcessingConfig


@dataclass(kw_only=True)
class EpochRunnerConfig(ArgsGroup):

    def __post_init__(self):
        ArgsGroup.__init__(
            self, "EpochRunnerConfig", "Arguments for the main training loop (EpochRunner)")
        # children configs
        self.grad_processing_config = GradProcessingConfig()

    turn_on_torch_amp_autocast: bool = BoolArg(
        "turn_on_torch_amp_autocast", action="store_true", default=False,
        help=f"Turn on torch's amp autocast. Default is False.",
        dynamic_defaults_dict=default_data_setting_dict
    )
    n_batches_per_epoch: int = IntArg(
        "n_batches_per_epoch", default=None,
        help="Maximum number of batches per epoch. This is useful primarily for really large datasets that even "
             "one epoch is too much and we wish to terminate training after a certain number of iterations."
             " This parameter interacts with n_accumulate_batches: if n_accumulate_batches=1, then total number of "
             "optimizer step per epoch is equal to this config. However, if n_accumulate_batches>1, then we must divide"
             " by n_accumulate_batches to get the total number of optimizer's steps."
    )

