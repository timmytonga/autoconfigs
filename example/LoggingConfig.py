from dataclasses import dataclass
from Arg import IntArg, StrArg, BoolArg
from ArgsGroup import ArgsGroup
from example.global_vars import default_data_setting_dict
from ConstraintCheckers import LowerBoundChecker
from example.ProfilerConfig import ProfilerConfig


@dataclass
class LoggingConfig(ArgsGroup):

    def __post_init__(self):
        ArgsGroup.__init__(self, "LoggingConfig", "Logging related configs")

    # should this inherit from LoggerConfig so that we can move the logging config to the logger?
    log_dir: str = StrArg(
        "log_dir", default="AUTO",
        help="Location to save log related files and checkpoints. Default: Auto dir"
    )
    log_fixed_gradients_n_epochs: int = IntArg(
        "log_fixed_gradients_n_epochs", default=0, type=int,
        help="The frequency (in epoch) to log gradients of batches as a epoch on its own."
             "Set this to > 0 to activate. For example, 1 would mean log gradients every epoch."
             "Enabling this would always log an epoch of gradients before training begins."
             "This will be more time consuming than log_gradients because of the additional epochs."
    )
    run_test_only_if_best_metric_split_improved: bool = BoolArg(
        "run_test_only_if_best_metric_split_improved", action="store_true", default=False,
        help="Turning this on will only run the test set on epochs when the metric for configured split"
             " improves. Modify config_best_metric and config_best_split to set the right metric"
             " for the right split (default to val accuracy)."
    )
    log_gradients: bool = BoolArg(
        "log_gradients", default=False, action="store_true",
        help="Log gradients of batches during training epoch"
    )
    log_every: int = IntArg(
        "log_every", type=int,
        help=f"Log every step. Default: 50.", default=50,
        dynamic_defaults_dict=default_data_setting_dict,
        constraint_check_fn=LowerBoundChecker(lower_bound=0, strict=True)
    )  # constraint > 0
    show_progress: bool = BoolArg(
        "show_progress", default=False, action="store_true",
        help="Show progress bar for training and validation."
    )
    # profiler related configs
    run_profiler: bool = BoolArg(
        "run_profiler", default=False, action="store_true",
        help="Turn on the profiler to profile for a set number of batches. "
             "See additional configs for profiler to control scheduler.",
        children_args={True: ProfilerConfig}
    )
