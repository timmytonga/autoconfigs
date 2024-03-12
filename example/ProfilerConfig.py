from dataclasses import dataclass
from Arg import IntArg
from ArgsGroup import ArgsGroup


@dataclass
class ProfilerConfig(ArgsGroup):
    def __post_init__(self):
        ArgsGroup.__init__(self, "ProfilerConfig", "Configs related to profiling runs",
                           field_name="profiler_config")

    wait: int = 5
    warmup: int = 2
    active: int = 3
    profile_memory: bool = True
    record_shapes: bool = True
    with_stack: bool = True

    schedule_skip_first: int = IntArg(
        "schedule_skip_first", default=5,
        help="Profiler's number of steps to skip before start profiling before starting profiler cycles.")

    repeat: int = IntArg(
        "repeat", default=1,
        help="Upperbound on the number of profiler cycles.")
