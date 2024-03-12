from dataclasses import dataclass
from Arg import BoolArg, StrArg, FloatArg
from ArgsGroup import ArgsGroup
from example.global_vars import default_data_setting_dict, default_scheduler_setting_dict


AVAIL_SCHEDULERS = ['linear', 'one_cycle', 'cos', 'reduce_lr_on_plateau']


@dataclass
class OneCycleLRConfig(ArgsGroup):
    field_name: str = 'one_cycle'

    def __post_init__(self):
        ArgsGroup.__init__(self, "OneCycleLRConfig", "OneCycleLR scheduler related configs",
                           field_name=self.field_name)

    max_lr: float = FloatArg(
        "max_lr", default=1,
        help="Maximum learning rate for the OneCycleLR scheduler."
    )
    anneal_strategy: str = StrArg(
        "anneal_strategy", choices=['cos', 'linear', 'none'], default='cos',
        help='Anneal strategy for OneCycleLR scheduler.'
    )
    pct_start: float = FloatArg(
        'pct_start', type=float, default=0.3,
        help=f"Warmup percent for OneCycleLR scheduler. "
             f"Default is: 0.3",  # fallback_value below
        dynamic_defaults_dict=default_data_setting_dict
    )
    no_cycle_momentum: bool = BoolArg(
        'no_cycle_momentum', action='store_true',
        help="Turns off cycle momentum for OneCycleLR scheduler."
    )


@dataclass
class SchedulerConfig(ArgsGroup):

    def __post_init__(self):
        ArgsGroup.__init__(self, "SchedulerConfig", "Scheduler related configs")

    scheduler: str = StrArg(
        "scheduler", choices=AVAIL_SCHEDULERS, default=None, help=f"Default is None.",
        dynamic_defaults_dict=default_data_setting_dict,
        children_args={'one_cycle': OneCycleLRConfig},
    )

    scheduler_step_every: str = StrArg(
        "scheduler_step_every", choices=['epoch', 'batch'], default='batch',
        help="Specify whether the scheduler step at every batch or every epoch. Typically most schedulers step after"
             " the optimizer steps, which is every _batch_. ",
        dynamic_defaults_dict=default_scheduler_setting_dict
    )
