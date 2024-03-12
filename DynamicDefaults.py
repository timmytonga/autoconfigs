from dataclasses import dataclass
from typing import List, Tuple, Dict, NewType, Union


ConfigType = NewType('ConfigType', Union[int, float, bool, str])
DYNAMIC_DEFAULT_FLAG = object()  # flag object to set dynamic default


@dataclass
class DynamicDefaults:
    """
    Class to store information for handling dynamic defaults
    Attributes: (example below are for setting default value for a model depending on the dataset)
        - default_field: This is the str indicating what the depending value should be
            E.g. 'dataset'
        - fallback_value: If the final depending_value is not specified then we set the value to this fallback_value
            E.g. 'resnet50'
        - default_map: list of pairs of mappings from depending field to default value.
            E.g. [(('mnist', 'cifar10'), 'resnet50'), (('imdb', 'mnli', 'sst2'), 'bert')]
            The above means that if the dataset is mnist or cifar10, the default model is resnet50. Similarly for bert.
    """
    default_field: str  # this is a string that specifies the field name to set defaults
    fallback_value: ConfigType  # this is the fallback value that will be used to set when not found
    default_map: List[Tuple[Tuple, ConfigType]]  # contains pairs of mapping
    # private attributes
    _dynamic_default_field_str = 'dynamic_default_field'

    def __post_init__(self):
        self._default_dict = {}
        for values, default in self.default_map:
            self._default_dict.update({value: default for value in values})

    def get_dynamic_default(self, depending_value) -> ConfigType:
        """
        Given the depending value, returns the corresponding dynamic default.
        """
        if depending_value in self._default_dict:
            return self._default_dict[depending_value]
        return self.fallback_value

    @staticmethod
    def get_default_map_from_default_dict(
            default_dict: Dict[str, Dict[str, ConfigType]],
            arg_name: str
    ) -> List[Tuple[Tuple, ConfigType]]:
        """
        Given a default_dict, create a default_map for all the arg_name
        """
        from collections import defaultdict
        tmp = defaultdict(list)
        for k, v in default_dict.items():
            if k == DynamicDefaults._dynamic_default_field_str:
                # this is metadata so we skip
                continue
            if isinstance(v, dict):
                if arg_name in v:
                    # if value is a dict we only get the value for the arg_name
                    tmp[v[arg_name]].append(k)
            else:
                tmp[v].append(k)
        return [(tuple(v), k) for k, v in tmp.items()]
