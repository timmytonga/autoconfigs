import argparse
from Arg import Arg, ConfigType
from DynamicDefaults import DynamicDefaults, DYNAMIC_DEFAULT_FLAG
from dataclasses import is_dataclass
from typing import Iterable, Tuple, List, Literal, Dict, ItemsView, Any, Union
from graphviz import Digraph  # to visualize the ArgsGroup tree. Can be useful for debugging.


class ArgsGroup:
    """
    A tree structure of args and configs. Each arg is of types defined in Arg.py as well as can be another ArgsGroup.
        Implements a bunch of iterator and method across the ArgsGroup tree (traverse and search nodes)
        Supports nice printing and args parsing
        Attributes that are not a subclass of ConfigType, Arg, or ArgsGroup will be ignored in most operations here.
    Some useful terms for this class
        - children: the attributes of this ArgsGroup node
        - all_children: attributes of this ArgsGroup node as well as attributes of children ArgsGroup
        - field: the string representation of an attribute
        - tree: refers to operations performing on all children FROM the root
            (e.g. search for something across all nodes)
    ArgsGroup contains 3 types of attributes: the iterators defined here are primarily for these 3 types
        - arg: attributes that are Arg
        - argsgroup: attributes that are ArgsGroup
        - config: attributes that are neither Arg nor children ArgsGroup
        *** there are some other special attributes. See get_sanitized_attributes_list method to see those.
    Method naming conventions:
        - get_*_to_*: getter method that returns a dictionary
        - get_*_list: getter method that returns a list
        - format_*: returns a nice string representation of * (useful for debugging and logging)
    Other terms:
        - root_argsgroup: the root of the ArgsGroup tree that this node belongs to
        - nested dictionary: a dictionary that contains another dictionary
        - flatten dictionary: not a nested dictionary
        - Dynamic default: a default that will be set at parsing time, where this default will be set depending on other
            args. E.g. optimizer=adamw is default if model=transformer vs. optimizer=adam if model=resnet50.
    """

    def __init__(self, name=None, description=None, field_name=None):
        assert name is not None, "Name for argsgroup should not be None"
        self.group_name = name
        self.group_description = description

        # private vars
        # parent ArgsGroup responsible for spawning this child ArgsGroup. If None then it is root.
        self._group_parent = None
        self._children_argsgroup = []
        self._field_name = field_name
        self._args_are_consumed = False
        self._root_argsgroup = None

    @property
    def root_argsgroup(self) -> 'ArgsGroup':
        """
        Returns the root of the ArgsGroup tree. Similar to get_root_argsgroup() but implements as a property to avoid
            recomputation.
        """
        if self._root_argsgroup is None:
            super().__setattr__('_root_argsgroup', self.get_root_argsgroup())
        return self._root_argsgroup

    def get_all_children_fields_to_values(self) -> Dict[str, Union[Arg, ConfigType]]:
        """
        Returns a flat dictionary that contains all the children fields along with their value
            - Their values can either be an Arg, ArgsGroup, or a config (non-arg or non-argsgroup attribute)
        """
        result = self.get_children_fields_to_values()
        for child in self.get_all_children_argsgroup():
            result.update(child.get_children_fields_to_values())
        return result

    def get_children_fields_to_values(self) -> Dict:
        """
        Returns a dictionary that contains the children fields along with their value
            - Their values are either an Arg or a config
        """
        result = {}
        for field in self.get_sanitized_attributes_list():
            value = getattr(self, field)
            # adds everything except ArgsGroup
            if isinstance(value, ArgsGroup):
                continue
            result[field] = value
        return result

    def get_value_from_field_in_tree(self, field) -> Union[Arg, ConfigType]:
        """
        Given a field for either an Arg or config, search across the entire tree
        """
        search_dict = self.root_argsgroup.get_all_children_fields_to_values()
        assert field in search_dict, f"Field {field} not in ArgsGroup tree."
        return search_dict[field]

    def add_children_args_to_parser(self, parser):
        """
        For each arg in ArgsGroup, add to parser
        """
        for arg in self.get_children_args():
            arg.add_arg_to_parser(parser)

    def set_children_args_to_default_values(self):
        """
        Iterate through all (remaining) children args and consume them i.e. set them to their default value
        This is typically called after we finish parsing to set the remaining args so that we have a finished config
        """
        for field, arg in self.get_children_args_items():
            # convert the value to the appropriate type if possible
            value = arg.type(arg.default) if isinstance(arg.default, arg.type) else arg.default
            setattr(self, field, value)

    def process_and_consume_args_with_namespace(self, namespace: argparse.Namespace) -> List['ArgsGroup']:
        """
        Given a corresponding namespace, given by an argparse, set the args appropriately including dynamic defaults.
            - either with the value given by the argparse's Namespace or if not available use the default values
        Will throw an error if the namespace contains a bad str.
        Returns:
            a list of children spawned ArgsGroup of self.
        """
        assert not self._args_are_consumed, \
            "_args_are_consumed is True! Should only call consume_args_with_argparse_namespace once after parsing."
        spawned_children_argsgroup = []
        children_args_dict = self.get_children_args_fields_to_value()
        for field in vars(namespace):
            assert field in children_args_dict, f"Invalid field {field} in namespace {namespace}"
            value = getattr(namespace, field)
            arg = children_args_dict[field]
            # process_value below performs type casting/checking and setting defaults
            if value == DYNAMIC_DEFAULT_FLAG:  # this means the user has not overridden the dynamic_default_flag
                value = self.get_dynamic_default_for_arg(arg)
            # then we sanitize the value (type casting, constraint checking, etc.)
            new_value = arg.sanitize_value_for_consumption(value)
            # now that we have a new value, we can spawn children if needed: attach to self and add to returned list
            self.spawn_args_children(arg, new_value, spawned_children_argsgroup)
            # finally we consume the arg and finish parsing it
            self.consume_arg(field, new_value)
        self.mark_self_as_parsed()
        return spawned_children_argsgroup

    def spawn_args_children(self, arg, new_value, spawned_children_argsgroup) -> None:
        """
        Get any constructor to spawn children ArgsGroup if needed and spawn it.
        Then attach it to self and append it to the spawned_children_argsgroup list for parsing later.
        """
        child_argsgroup_to_spawn = arg.spawn_children_args(new_value)
        if child_argsgroup_to_spawn is not None:
            # first spawn the child and let it know that self is the parent
            spawned_child_argsgroup = child_argsgroup_to_spawn()
            childs_field_name = spawned_child_argsgroup.get_field_name()
            assert childs_field_name is not None, \
                "Children argsgroup need to have a field_name init in config class def's ArgsGroup.__init__"
            assert childs_field_name not in self.get_children_fields_to_values().keys(), \
                f"Children argsgroup's field_name (={childs_field_name}) already exists!"
            # attach the child to this group so the parent know the child
            setattr(self, childs_field_name, spawned_child_argsgroup)
            spawned_children_argsgroup.append(spawned_child_argsgroup)

    def get_field_name(self):
        return self._field_name

    def mark_self_as_parsed(self):
        """
        Reset some properties after parsed
        """
        self._args_are_consumed = True

    def get_dynamic_default_for_arg(self, arg: Arg):
        assert isinstance(arg.dynamic_default, DynamicDefaults)
        # now we try to find the appropriate value
        default_field = arg.dynamic_default.default_field
        default_value = self.get_value_from_field_in_tree(default_field)
        assert not isinstance(default_value, Arg), \
            f"Default field {default_field} must be consumed before setting dependent Arg {arg.get_name()}."
        return arg.dynamic_default.get_dynamic_default(default_value)

    def consume_arg(self, field, new_value):
        """
        Consume the arg with name field and set it to new_value. After calling this, we will lose the Arg.
        """
        setattr(self, field, new_value)

    def get_new_parser(self) -> argparse.ArgumentParser:
        """
        Initializes a parser.
        Loops through attributes in dataclass and if it is an instance of Arg,
        add it to the parser.
        """
        parser = argparse.ArgumentParser(prog=self.get_name(), description=self.get_description())
        self.add_children_args_to_parser(parser)
        return parser

    def get_all_children_argsgroup(self, ordering: Literal['dfs', 'bfs'] = 'dfs', reverse=False) -> List['ArgsGroup']:
        """
        Returns a list of args that are ArgsGroup in the specified ordering
        """
        if ordering == 'dfs':
            result = self._get_all_children_argsgroup_dfs()
        elif ordering == 'bfs':
            result = self._get_all_children_argsgroup_bfs()
        else:
            raise NotImplementedError(f"Unknown ordering: {ordering}")
        if reverse:
            result.reverse()
        return result

    def _get_all_children_argsgroup_dfs(self) -> List['ArgsGroup']:
        my_children = self.get_children_argsgroup()
        result = []
        for child in my_children:
            result.append(child)
            result.extend(child._get_all_children_argsgroup_dfs())
        return result

    def _get_all_children_argsgroup_bfs(self) -> List['ArgsGroup']:
        from collections import deque
        my_children = self.get_children_argsgroup()
        visit_queue = deque(my_children)
        result = []
        while len(visit_queue) > 0:
            child = visit_queue.popleft()
            result.append(child)
            visit_queue.extend(child.get_children_argsgroup())
        return result

    def get_children_argsgroup(self) -> List['ArgsGroup']:
        return self._children_argsgroup

    def get_children_args(self) -> List[Arg]:
        """
        Returns the current list of children args
        """
        result = []
        for field in self.get_sanitized_attributes_list():
            value = getattr(self, field)
            if isinstance(value, Arg):
                result.append(value)
        return result

    def get_children_args_fields_to_value(self) -> Dict[str, Arg]:
        """
        Returns the dictionary containing key fields and value Arg
        """
        result = {}
        for field in self.get_sanitized_attributes_list():
            value = getattr(self, field)
            if isinstance(value, Arg):
                result[field] = value
        return result

    def get_all_children_configs_to_self(self) -> Dict[str, 'ArgsGroup']:
        """
        Recursively get all children configs dict with self. This is useful to set default values.
        Returns the dictionary containing key fields and value self for ALL children args.
        """
        result = {field: self for field in self.get_configs_fields_list()}
        for child in self.get_all_children_argsgroup():
            childs_dict = {field: child for field in child.get_configs_fields_list()}
            assert not (set(result.keys()) & set(childs_dict.keys())), \
                ("We cannot call get_all_configs_to_self_dict if there are keys' collision.\n"
                 f"result: {result.keys()}\nchilds_dict: {childs_dict.keys()}")
            result.update(childs_dict)
        return result

    def get_configs_to_value(self) -> Dict[str, Any]:
        """
        Returns a dictionary representation of the non-args configs in this ArgsGroup
        """
        result = {}
        for field in self.get_configs_fields_list():
            result[field] = getattr(self, field)
        return result

    def get_all_configs_to_value(self) -> Dict[str, Any]:
        """
        Returns a dictionary representation of ALL the non-args configs in the ArgsGroup tree
        Useful for logging configs to wandb and as an intermediate representation to export to say JSON
        """
        result = self.get_configs_to_value()
        for child in self.get_children_argsgroup():
            result[child.get_name()] = child.get_all_configs_to_value()
        return result

    def get_flattened_all_configs_to_value(self) -> Dict:
        """
           Returns a _flattened_ dictionary representation of ALL the non-args configs in the ArgsGroup tree
           Useful for logging configs to wandb and as an intermediate representation to export to say JSON
        """
        result = self.get_configs_to_value()
        for child in self.get_all_children_argsgroup():
            result.update(child.get_configs_to_value())
        return result

    def load_configs_from_dict(self, cfg_dict: dict):
        """
        Another way to initialize an ArgsGroup tree is via a dictionary (as opposed to parsing).
        Can be useful to load configs from a file
        TODO
        """
        pass

    def get_children_args_items(self) -> ItemsView[str, Arg]:
        """
        Returns the key value pair: field, Arg
        """
        return self.get_children_args_fields_to_value().items()

    def get_num_args(self) -> int:
        return len(self.get_children_args())

    def get_num_argsgroup(self) -> int:
        return len(self.get_children_argsgroup())

    def get_parent_argsgroup(self):
        """
        Return the parent ArgsGroup or None if self is a root ArgsGroup.
        """
        return self._group_parent

    def get_root_argsgroup(self):
        """
        Return the root argsgroup.
        """
        if self.get_parent_argsgroup() is None:
            return self
        return self.get_parent_argsgroup().get_root_argsgroup()

    def format_attributes(self, include_children_argsgroup=True) -> str:
        """
        Return a nice string representation of all the Args within this ArgsGroup
        """
        name = self.get_name()
        parent_name = self.get_parent_argsgroup().get_name() if self.get_parent_argsgroup() is not None else 'ROOT'
        parent_str = f"{parent_name}" if parent_name == "ROOT" else f"parent: {parent_name}"
        description = f"{self.get_description()}\n\t*** {self.format_stats()} ***"
        result_str = f"{name} ({parent_str}): {description}\n"
        for field in self.get_sanitized_attributes_list():
            value = getattr(self, field)
            if isinstance(value, Arg):
                result_str += f"\t(Arg)\t{value.format_description()}"
            elif isinstance(value, ArgsGroup):
                if include_children_argsgroup:
                    result_str += f"\t(ArgsGroup) {value.format_description()}\n"
            else:
                if value is None:
                    result_str += f"\t[None]"
                else:
                    result_str += f"\t[{type(value).__name__}]"
                result_str += f"\t{field}:\t"
                result_str += f"{str(value)}"
                result_str += "\n"
        result_str += "\n"
        return result_str

    def format_description(self):
        result = self.get_name() if self.get_field_name() is None else self.get_field_name()
        return f"{result}:\t{self.format_stats()}"

    def format_stats(self):
        num_args = self.get_num_args()
        result = f"{num_args} Args, " if num_args > 0 else ""
        noncfg_str = "non-Arg configs" if num_args > 0 else "configs"
        result += f"{self.get_num_configs()} {noncfg_str}, "
        num_argsgroup = self.get_num_argsgroup()
        result += f"{num_argsgroup} ArgsGroup."
        return result

    def format_flatten_attributes(self, ordering: Literal['bfs', 'dfs'] = 'bfs', include_children_argsgroup=False):
        """
        String representation of ArgsGroup consists of the flattened out verion of all the args and nested ArgsGroup.
        The args are grouped the by ArgsGroup.
        """
        result_str = self.format_attributes(include_children_argsgroup)
        children_args_group = self.get_all_children_argsgroup(ordering=ordering)
        for child in children_args_group:
            assert isinstance(child, ArgsGroup)
            result_str += child.format_attributes(include_children_argsgroup)
        return result_str

    def __str__(self):
        return self.format_attributes(include_children_argsgroup=True)

    def get_all_self_field_arg(self) -> Iterable[Tuple['ArgsGroup', str, Arg]]:
        """
        Similar to dict.items() but the ordering here is DFS order of the ArgsGroup (where we get all the Args inside
            an ArgsGroup before moving towards the next node).
        Return: A tuple of (self, field, Arg). We return self because it might be useful to know which field belongs
            to which ArgsGroup. This allows for potential modification of Arg during parsing.
        """
        children_args_group = []
        for field in self.get_sanitized_attributes_list():
            value = getattr(self, field)
            if isinstance(value, Arg):
                yield self, field, value
            elif isinstance(value, ArgsGroup):
                children_args_group.append(value)
        for child in children_args_group:
            yield from child.get_all_self_field_arg()

    def get_configs_fields_list(self) -> List[str]:
        """
        Return a list of fields of ArgsGroup where the fields are neither Arg nor ArgsGroup
        """
        tmp = [field for field in self.get_sanitized_attributes_list()]

        def nonargs_and_argsgroup(x):
            return not (isinstance(getattr(self, x), Arg) or isinstance(getattr(self, x), ArgsGroup))

        result = filter(nonargs_and_argsgroup, tmp)
        return list(result)

    def get_num_configs(self) -> int:
        return len(self.get_configs_fields_list())

    def get_name(self):
        return self.group_name

    def get_description(self):
        return self.group_description

    def get_sanitized_attributes_list(self) -> List[str]:
        """
        Returns a sanitized list of fields defined by the exclude_attributes list below.
        """
        assert is_dataclass(self), "Children of ArgsGroup should be of class dataclass"
        # add more attributes below to exclude
        exclude_attributes = ['group_name', 'group_parent', 'group_description', 'field_name']

        def filter_attributes(val) -> bool:
            if val in exclude_attributes:
                return False
            if val[0] == '_':  # exclude private attributes
                return False
            return True

        result = list(filter(filter_attributes, vars(self).keys()))
        return result

    def _set_parent(self, parent):
        assert self._group_parent is None, "This method should be called only once. When do we want to change parents?"
        # we must call super's setattr otherwise we will loop.
        super().__setattr__('_group_parent',  parent)

    def __setattr__(self, name, value):
        # Call the original __setattr__ to set the attribute
        super().__setattr__(name, value)

        # If the attribute being set is an instance of ArgsGroup
        if isinstance(value, ArgsGroup):
            # Add the child to the current instance's children list
            self._children_argsgroup.append(value)
            # Set the parent of the child to the current instance
            value._set_parent(self)

    def draw_tree_from_me(self, dot=None) -> Digraph:
        """
        Uses graphviz library to draw the ArgsGroup tree where each node contains the name of the ArgsGroup.
        To use the returned Digraph, run:
            dot = root_conf.draw_tree_from_me()
            dot.render('root_conf_tree', format='png', cleanup=True)
        where root_conf is the root ArgsGroup.
        """
        if dot is None:
            dot = Digraph(comment="Tree visualization")
        dot.node(self.get_name(), label=f"{self.get_name()}\n{self.format_stats()}")
        for child in self.get_children_argsgroup():
            child.draw_tree_from_me(dot)
            dot.edge(self.get_name(), child.get_name())
        return dot


def pretty_str_list_of_argsgroup(agl: List['ArgsGroup']) -> str:
    if len(agl) == 0:
        return "[]"
    result = f"[{agl[0].get_name()}"
    for i in range(1, len(agl)):
        result += f", {agl[i].get_name()}"
    result += "]"
    return result
