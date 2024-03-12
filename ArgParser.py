"""
Parse a tree of ArgsGroup, starting from a given root.

For each ArgsGroup, create a new argument group if the argsgroup_name or description is not none
"""

from ArgsGroup import ArgsGroup
import argparse
from typing import Dict, Any


def parse_and_process_argsgroup(argsgroup: ArgsGroup, root_parser, rem_args) -> list[str]:
    """
    Adds group to root parser (as an argument group), create new parser to parse and store to argsgroup.
    This function modifies the rem_args by parsing the known args there and modifying rem_args
    """
    # first we add the group to the root parser for printing out help messages
    group = root_parser.add_argument_group(argsgroup.get_name(), argsgroup.get_description())
    argsgroup.add_children_args_to_parser(group)
    # we don't parse with the main parser though. we parse each namespace individually
    group_parser = argsgroup.get_new_parser()
    namespace, rem_args = group_parser.parse_known_args(rem_args)
    # consume the args.
    spawned_children_argsgroup = argsgroup.process_and_consume_args_with_namespace(namespace)
    # if there is any spawned children argsgroup, parse and process them
    for child in spawned_children_argsgroup:
        rem_args = parse_and_process_argsgroup(child, root_parser, rem_args)
    # then we return the rem_args
    return rem_args


class ArgParser:
    def __init__(self, root: ArgsGroup):
        """
        Initialize a parser that parses an ArgsGroup tree from root.
        To use dynamic defaults, set default in Arg to DYNAMIC_DEFAULT and fill out the Arg's setting in default_dict
             and fallback_dict.
        :param root: The root of the ArgsGroup tree
        """
        self.root = root
        # private properties
        self._have_parsed_root_flag = False

    def parse_args_recursively(self, parse_str=None) -> argparse.ArgumentParser:
        """
        Main method to parse args. Parse args recursively from the root in a BFS manner.
            Consume defaults or set defaults dynamically.
        """
        parser = self.get_init_root_parser()
        # first add the args from root
        group = parser.add_argument_group(self.root.get_name(), self.root.get_description())
        self.root.add_children_args_to_parser(group)
        # then parse known args
        if parse_str is None:
            namespace, rem_args = parser.parse_known_args()
        else:  # this case should be mainly for testing
            namespace, rem_args = parser.parse_known_args(parse_str.split())
        # then we consume the args for the root
        self.root.process_and_consume_args_with_namespace(namespace)
        # then add all args from children and parse
        all_argsgroup_from_root_bfs = self.root.get_all_children_argsgroup(ordering='bfs')
        for argsgroup in all_argsgroup_from_root_bfs:
            rem_args = parse_and_process_argsgroup(argsgroup, parser, rem_args)

        if len(rem_args) > 0:
            raise argparse.ArgumentError(None, f"Too many args. See help below: "
                                               f"\n{parser.format_help()}")
        self._have_parsed_root_flag = True
        return parser

    def get_flattened_parser(self):
        """
        Parse the ArgsGroup tree starting from self.root in a BFS manner.
        This is mainly for testing purposes only
        """
        parser = self.get_init_root_parser()
        # first add the args from root
        group = parser.add_argument_group(self.root.get_name(), self.root.get_description())
        self.root.add_children_args_to_parser(group)
        # then add all args from children
        all_argsgroup_from_root_bfs = self.root.get_all_children_argsgroup(ordering='bfs')
        for argsgroup in all_argsgroup_from_root_bfs:
            group = parser.add_argument_group(argsgroup.get_name(), argsgroup.get_description())
            argsgroup.add_children_args_to_parser(group)
        return parser

    @staticmethod
    def get_init_root_parser(prog_name='fastr') -> argparse.ArgumentParser:
        description = """
        pipeline for ML/DL research in a modularized format that allows for easy modification and addition. 
        This repo also aims to minimize the amount of system configurations needed to start training."""
        arg_parser = argparse.ArgumentParser(
            prog=prog_name,
            description=description,
            allow_abbrev=False,
            parents=[],
        )
        return arg_parser
