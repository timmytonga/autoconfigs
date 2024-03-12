"""
Argument class definition for specifying argument dependencies and parsing to be used with Python's argparse
"""
import argparse
from typing import Callable, Union, Type, Dict
from dataclasses import dataclass

from DynamicDefaults import DynamicDefaults, ConfigType, DYNAMIC_DEFAULT_FLAG


@dataclass
class Arg:
    """
    Arg class to handle arguments constraints and dependencies. Helps with adding only necessary args.
    """
    # basic args fields
    name: str
    # setting this to DYNAMIC_DEFAULT will set the default value according to the default_args_dict
    default: ConfigType = None
    # optional args fields
    help: str = ""
    action: str = None
    choices: list = None
    nargs: int = None
    type: type = None
    # advanced args fields to manage dependencies between Args
    constraint_check_fn: Callable[[ConfigType], bool] = None
    dependencies: dict = None  # this narrows down the possible choices an Arg can take on depending on other args
    # this spawns children ArgsGroup when a selection is chosen
    children_args: Dict[ConfigType, Type] = None
    # dynamic_defaults are primarily handled in ArgsGroup.get_dynamic_default_for_arg
    dynamic_defaults_dict: Dict = None
    # some other helper vars
    _valid_actions = ['store_true', 'store_false', 'store']

    def __post_init__(self):
        assert self.type is not None, "Must set the type in children class or explicitly"
        assert len(self.name) > 1, "Abbreviations are not allowed (for now)."
        assert self.action is None or self.action in self._valid_actions, \
            f"action can only be within {self._valid_actions}"
        # dynamic defaults setting
        self.dynamic_default = None
        if self.dynamic_defaults_dict is not None:
            self.dynamic_default = DynamicDefaults(
                default_field=self.dynamic_defaults_dict['dynamic_default_field'],
                default_map=DynamicDefaults.get_default_map_from_default_dict(self.dynamic_defaults_dict, self.name),
                fallback_value=self.default
            )
            self.default = DYNAMIC_DEFAULT_FLAG  # set default to this object so we know when user passes new value

    def add_dependencies(self, dependencies: dict):
        if self.dependencies is None:
            self.dependencies = dependencies
        else:
            self.dependencies.update(dependencies)

    def get_arg_dict(self) -> dict:
        """
        Returns a dictionary that contains all the information to pass into argparse's add_argument
        """
        arg_dict = {'help': self.help, 'default': self.default}
        if self.action is not None:
            arg_dict['action'] = self.action
        if self.choices is not None:
            arg_dict['choices'] = self.choices
        if self.nargs is not None:
            arg_dict['nargs'] = self.nargs

        return arg_dict

    def add_arg_to_parser(self, parser: argparse.ArgumentParser):
        parse_name = self.name if self.name[0] == '-' and self.name[1] == '-' else f'--{self.name}'
        parser.add_argument(f"{parse_name}", **self.get_arg_dict())

    def get_name(self):
        return self.name

    def get_new_arg_with_new_value(self, new_value):
        return Arg(self.name, default=new_value, help=self.help, action=self.action,
                   choices=self.choices, nargs=self.nargs,
                   type=self.type, constraint_check_fn=self.constraint_check_fn, dependencies=self.dependencies,
                   children_args=self.children_args)

    def __hash__(self):
        return hash(f"{self.name}{self.help}{str(self.type)}")

    def __str__(self):
        return f"{str(self.default)}"

    def format_description(self) -> str:
        result = f"{self.name}:\t"
        result += f"'{str(self)}'\n" if isinstance(self, StrArg) else f"{str(self)}\n"
        return result

    def cast_value_to_arg_type(self, value):
        """
        Since the value given by an argparser is typically a str, we try to cast things here
        Given a value, typically either from the user setting the Arg or the parser setting the default,
            depending on what the value is (a normal value, None, DYNAMIC_DEFAULT) we either cast it to correct type or
            set it to some default value.
        """
        if value is None:
            new_value = value
        else:
            new_value = self.type(value)
        return new_value

    def get(self, name):
        # need to check anything?
        return getattr(self, name)

    def check_constraint(self, value) -> bool:
        """
        Check if user input value is valid according to the constraint_check_fn
        """
        if self.constraint_check_fn is not None:
            return self.constraint_check_fn(value)
        return True

    def get_dynamic_default_value(self, value):
        raise NotImplementedError

    def sanitize_value_for_consumption(self, value):
        """
        Arg constraint checking and type casting
        Sanitize the value given by the namespace
        """
        new_value = self.cast_value_to_arg_type(value)
        # check type
        assert isinstance(new_value, self.type) or (new_value is None), \
            f"Invalid value {new_value} type {type(new_value)} where arg.type is {self.type} for arg {self.name}."
        # then we check constraint
        self.check_constraint(new_value)
        # check another implicit constraint
        if value is not None and self.choices is not None and len(self.choices) >= 1:
            assert value in self.choices, f"Received value (={value}) that are not in choices (={self.choices})."
        return new_value

    def spawn_children_args(self, value: ConfigType) -> Union[Type, None]:
        """
        This should be called after we have a value to be prepared for consumption.
        Depending on what the final value is,
            returns an ArgsGroup subclass to be constructed.
        """
        if self.children_args is None:
            return None
        if value in self.children_args:
            return self.children_args[value]
        return None


class IntArg(Arg):
    def __post_init__(self):
        self.type = int
        super().__post_init__()


class StrArg(Arg):
    def __post_init__(self):
        self.type = str
        super().__post_init__()


class FloatArg(Arg):
    def __post_init__(self):
        self.type = float
        super().__post_init__()


class BoolArg(Arg):
    def __post_init__(self):
        self.type = bool
        super().__post_init__()
