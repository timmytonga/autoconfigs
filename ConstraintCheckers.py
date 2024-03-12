"""
Constraints classes with error messages and warning messages
"""
from abc import ABC, abstractmethod


class ConstraintChecker(ABC):
    """
    Base class for all the constraint functions.
    This provides simple template to create functions that checks and prints out appropriate message and warning
    """
    @abstractmethod
    def __call__(self, value):
        pass


class LowerBoundChecker(ConstraintChecker):
    def __init__(self, lower_bound, strict=False):
        self.lower_bound = lower_bound
        self.strict = strict

    def __call__(self, value):
        if self.strict and value <= self.lower_bound:
            raise ValueError(f"Value {value} is less than or equal to the lower bound {self.lower_bound}")
        elif not self.strict and value < self.lower_bound:
            raise ValueError(f"Value {value} is less than the lower bound {self.lower_bound}")
        return value


class UpperBoundChecker(ConstraintChecker):
    def __init__(self, upper_bound, strict=False):
        self.upper_bound = upper_bound
        self.strict = strict

    def __call__(self, value):
        if self.strict and value >= self.upper_bound:
            raise ValueError(f"Value {value} is greater than or equal to the upper bound {self.upper_bound}")
        elif not self.strict and value > self.upper_bound:
            raise ValueError(f"Value {value} is greater than the upper bound {self.upper_bound}")
        return value


class CompositeConstraintChecker(ConstraintChecker):
    def __init__(self, checkers):
        self.checkers = []
        self.lower_bounds = []
        self.upper_bounds = []

        for checker in checkers:
            if isinstance(checker, LowerBoundChecker):
                self.lower_bounds.append((checker.lower_bound, checker.strict))
            elif isinstance(checker, UpperBoundChecker):
                self.upper_bounds.append((checker.upper_bound, checker.strict))

        self.lower_bounds.sort(key=lambda x: (x[0], not x[1]))
        self.upper_bounds.sort(key=lambda x: (x[0], x[1]))

        if self.lower_bounds and self.upper_bounds:
            max_lower_bound, max_lower_strict = self.lower_bounds[-1]
            min_upper_bound, min_upper_strict = self.upper_bounds[0]

            if max_lower_bound >= min_upper_bound:
                if max_lower_strict and min_upper_strict:
                    raise ValueError(
                        f"Incompatible constraints: lower bound {max_lower_bound} >= upper bound {min_upper_bound}")
                elif max_lower_strict and not min_upper_strict:
                    raise ValueError(
                        f"Incompatible constraints: lower bound {max_lower_bound} > upper bound {min_upper_bound}")
                elif not max_lower_strict and min_upper_strict:
                    raise ValueError(
                        f"Incompatible constraints: lower bound {max_lower_bound} >= upper bound {min_upper_bound}")

        if self.lower_bounds:
            max_lower_bound, strict = self.lower_bounds[-1]
            self.checkers.append(LowerBoundChecker(max_lower_bound, strict))

        if self.upper_bounds:
            min_upper_bound, strict = self.upper_bounds[0]
            self.checkers.append(UpperBoundChecker(min_upper_bound, strict))

    def __call__(self, value):
        for checker in self.checkers:
            value = checker(value)
        return value
