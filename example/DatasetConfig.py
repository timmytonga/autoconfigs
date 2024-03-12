from dataclasses import dataclass
from Arg import IntArg, StrArg, FloatArg, BoolArg
from ArgsGroup import ArgsGroup
from example.global_vars import default_data_setting_dict


AVAIL_DATASETS = ['mnist', 'cifar10', 'wikitext', 'sst2', 'imdb', 'mrpc', 'mnli']
MAX_NUM_WORKERS = 4


@dataclass
class DatasetConfig(ArgsGroup):

    def __post_init__(self):
        ArgsGroup.__init__(
            self, "DatasetConfig", "Arguments for data loading and preprocessing")

    dataset: str = StrArg(
        "dataset", choices=AVAIL_DATASETS, default='cifar10'
    )
    val_fraction: float = FloatArg(
        "val_fraction", default=0,
        help="Fraction of the training dataset to split for validation."
    )
    # dataloader configs
    num_workers: int = IntArg(
        "num_workers", default=MAX_NUM_WORKERS,
        help=f"Set the number of workers to help with dataloading. "
             f"Default is MAX_NUM_WORKERS={MAX_NUM_WORKERS}. Can set to be less than MAX_NUM_WORKERS"
             f"but cannot exceed! Change MAX_NUM_WORKERS in global_vars.py"
    )
    batch_size: int = IntArg(
        "batch_size", help="See also n_accumulate_batches.", default=256,
        dynamic_defaults_dict=default_data_setting_dict

    )
    n_accumulate_batches: int = IntArg(
        "n_accumulate_batches", default=1,
        help='Set this number greater than 1 in order to accumulate gradients across multiple batches before taking an '
             'optimizer step. For example, if your hardware cannot handle a batch_size of 32 but you want to step with '
             'batch_size 32, you can instead set (batch_size=16 and acc_steps=2) or (batch_size=8 and acc_steps=4) or '
             'any other combinations to get the same effect. The only downside is that you will lose parallelization. ',
        dynamic_defaults_dict=default_data_setting_dict
    )
    no_augment_data: bool = BoolArg(
        "no_augment_data", action="store_true", default=False,
        help="Set this flag to not run data augmentation."
    )
