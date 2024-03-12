from dataclasses import dataclass
from example.GPTBaseConfigs import GPTBaseConfigs
from Arg import StrArg, FloatArg, BoolArg
from ArgsGroup import ArgsGroup
from example.global_vars import default_data_setting_dict


AVAIL_MODELS = ['resnet50', 'gptbase', 'bert']


@dataclass
class ModelConfig(ArgsGroup):
    def __post_init__(self):
        ArgsGroup.__init__(self, "ModelConfig", "Model related configs")

    model: str = StrArg(
        "model", choices=AVAIL_MODELS, default='resnet50',
        dynamic_defaults_dict=default_data_setting_dict,
        children_args={'gptbase': GPTBaseConfigs},
    )
    dropout: float = FloatArg(
        "dropout", type=float, default=0,
        help="Set the dropout rate for models that use them. ***Warning***: This doesn't work with all"
             "models. Check the model code before setting this!!",
        dynamic_defaults_dict=default_data_setting_dict
    )
    use_pretrained: bool = BoolArg(
        "use_pretrained", action="store_true", default=False,
        help="Set this to use pretrained model for certain available models. Don't think this works yet though."
    )
