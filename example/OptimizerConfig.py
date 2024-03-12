from dataclasses import dataclass
from Arg import StrArg, FloatArg
from example.global_vars import default_data_setting_dict

from ArgsGroup import ArgsGroup


AVAIL_OPTIMIZERS = ['sgd', 'adam', 'adamw']


@dataclass
class OptimizerConfig(ArgsGroup):

    def __post_init__(self):
        ArgsGroup.__init__(self, "OptimizerConfig", "Optimizer related configs")

    optimizer: str = StrArg(
        "optimizer", choices=AVAIL_OPTIMIZERS, default='sgd',
        dynamic_defaults_dict=default_data_setting_dict
    )

    lr: float = FloatArg(
        "lr", help=f"Learning Rate.", default=1e-3,
        dynamic_defaults_dict=default_data_setting_dict
    )
    weight_decay: float = FloatArg(
        "weight_decay", help=f"L2 Regularization.", default=0,
        dynamic_defaults_dict=default_data_setting_dict
    )
