from dataclasses import dataclass
from Arg import FloatArg
from ArgsGroup import ArgsGroup


@dataclass(kw_only=True)
class GradProcessingConfig(ArgsGroup):

    def __post_init__(self):
        ArgsGroup.__init__(
            self, "GradProcessingConfig", "Gradient Processing Configs")

    # gradient clipping and adding noise
    scale_noise: float = FloatArg(
        "scale_noise", default=1,
        help="When noise is being added per-coordinate, this parameter scales down the noise. "
             "This can be useful in scenario like wanting to scale down the noise so that the total "
             "noise added is not dependent on the dimension."
    )
    clip_grad: float = FloatArg(
        "clip_grad", type=float, default=None,
        help="Set the threshold to clip grad norm before stepping. Default is (None) "
             "which means no clipping will be employed. The norm is calculated across the whole model "
             "and the gradient is clipped accordingly to the whole model (and not just layer by layer)"
    )
    noise_param: float = FloatArg(
        "noise_param", type=float, default=None,
        help="Specify the noise_param for the specified noise distribution from noise_name. "
             "If noise_name is None, this argument will be ignored. "
             "For example, if noise_name is Laplace, "
             "then this noise_param determines the param b (see Wiki page) for Laplace distribution"
    )
