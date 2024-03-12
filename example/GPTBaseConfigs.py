from dataclasses import dataclass
from ArgsGroup import ArgsGroup
from Arg import IntArg
from example.global_vars import default_data_setting_dict


@dataclass
class GPTBaseConfigs(ArgsGroup):
    field_name: str = 'gpt_base_configs'

    def __post_init__(self):
        ArgsGroup.__init__(self, "GPTBaseConfigs", "GPTBase models' configs",
                           field_name=self.field_name)

    vocab_size: int = 50304
    n_embd: int = 768
    # Language modeling configs
    sequence_length: int = IntArg(
        'sequence_length', default=512,
        help="Max sequence length for model. Used to truncate or pad data. Default is 512}",
        dynamic_defaults_dict=default_data_setting_dict
    )
    bias: bool = False
    n_layer: int = IntArg(name="n_layer", default=12, help="Set n_layer for GPTBase model. Default is 12.")
    n_head: int = IntArg(name="n_head", default=4, help="Set n_head for GPTBase model. Default is 4.")
    dtype = float
    # Arg(name="dtype", default=torch.bfloat16, type=torch.dtype,
    #                      help="Set the training type for GPTBase model. Default is torch.bfloat16."))
    dropout: float = 0.2
