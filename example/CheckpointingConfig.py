from dataclasses import dataclass
from typing import Literal

from Arg import BoolArg, StrArg
from ArgsGroup import ArgsGroup


AVAIL_METRICS = ['accuracy', 'loss']


@dataclass
class CheckpointingConfig(ArgsGroup):

    def __post_init__(self):
        ArgsGroup.__init__(self, "CheckPointingConfig", "Configs for checkpointing")

    save_last: bool = BoolArg("save_last", action="store_true", default=False)
    save_best: bool = BoolArg(
        "save_best", action="store_true", default=False,
        help="Save the best model according to specified metric and split."
    )  # store true
    config_best_split: Literal['val', 'train'] = StrArg(
        "config_best_split", choices=['train', 'val'], default="val",
        help="Select the split (train or val) to save the best model according to config_best_metric. "
             "Default to val."
    )
    config_best_metric: Literal['accuracy', 'loss'] = StrArg(
        "config_best_metric", choices=AVAIL_METRICS, type=str, default="accuracy",
        help=f"Pick a metric from {AVAIL_METRICS} as the main metric to save the best model."
             f"This works with the argument `config_best_split` (default to val) to save."
    )
    resume: bool = BoolArg(
        "resume", action="store_true", default=False,
        help="Resume training from the last checkpoint."
    )
    # Non-Args attributes
    wandb_id: str = None  # this should be set by main
