from dataclasses import dataclass
from Arg import BoolArg, StrArg, IntArg  # todo: refactor _DEFAULT to some other name
from ArgsGroup import ArgsGroup

# children configs
from example.ModelConfig import ModelConfig
from example.TrainerConfig import TrainerConfig
from example.DatasetConfig import DatasetConfig


@dataclass
class MainConfig(ArgsGroup):
    """
    Root config for project
    """

    def __post_init__(self):
        # parent=None means I am the root
        ArgsGroup.__init__(self, "MainConfig", "Main Configs for the project")
        # the ordering of these children configs matter because of default creation dependency
        self.dataset_config: DatasetConfig = DatasetConfig()
        self.model_config: ModelConfig = ModelConfig()
        # since some of the TrainerConfig's Arg depends on the dataset's configs, we need to initialize it after.
        self.trainer_config: TrainerConfig = TrainerConfig()

    # first some project configs
    project_name: str = StrArg(
        "project_name", default="PROJECT_NAME",
        help="wandb project name. modify default in global_vars.py"
    )
    wandb: bool = BoolArg(
        "wandb", action="store_true", default=False,
        help="Turn on wandb logging which is a cloud-based logging and visualization app."
             "See more info at wandb.ai."
    )
    wandb_entity: str = StrArg(
        "wandb_entity", type=str, default='fastr',
        help="wandb entity name. An entity can be a team or an individual. Use the team's name if"
             " the project is within the team. "
    )
    gpu: int = IntArg(
        'gpu', type=int, default=0, help="Set gpu to -1 to use cpu instead"
    )
    seed: int = IntArg(
        "seed", type=int, default=None,
        help=f"Set deterministic seed. Default: None i.e. random seed."
    )
