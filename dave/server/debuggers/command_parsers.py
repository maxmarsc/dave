from __future__ import annotations
from argparse import ArgumentParser, Namespace, ArgumentError
from abc import ABC, abstractmethod
import types

from dave.common.logger import Logger
from typing import Union, override


class ParsingError(Exception):
    pass


class DaveArgumentParser(ArgumentParser, ABC):
    """
    Custom workaround class, see https://github.com/python/cpython/issues/103498
    """

    def __init__(self, subprog: str, **kwargs):
        super().__init__(prog=f"dave {subprog}", **kwargs)
        # override method error
        self.error = types.MethodType(DaveArgumentParser.__non_exiting_error, self)

    @property
    def subprog(self) -> str:
        return self.prog.split()[1]

    @property
    def usage_property(self) -> str:
        # Delete the \n at the end
        return self.format_usage()[:-1]

    def __non_exiting_error(self, message):
        raise ParsingError(message)


class ShowCommandParser(DaveArgumentParser):
    def __init__(self):
        super().__init__(
            "show", usage="usage: dave show [-h] [--dims DIM1 [DIM2]] [VARIABLE]"
        )
        self.add_argument(
            "VARIABLE",
            help="Name of the variable to show on the gui. If not provided dave will show every "
            "compatible variable in the current frame.",
            type=str,
            nargs="?",
        )
        self.add_argument(
            "--dims",
            nargs="+",
            help="Dimensions in format DIM1 [DIM2]. Required for pointer-like types. 2 dimensions is expected for pointers of pointers. Caution : If no variable name was provided these dimensions will apply to every pointer-like entity.",
            default=[],
            type=int,
        )


class InspectCommandParser(DaveArgumentParser):
    def __init__(self):
        super().__init__("inspect")
        self.add_argument("VARIABLE", help="Name of the variable to inspect", type=str)


class DeleteCommandParser(DaveArgumentParser):
    def __init__(self):
        super().__init__("delete")
        self.add_argument(
            "VARIABLE_ID",
            help="Name/ID of the variable to delete from the gui. "
            "When providing a conflicting name, the first entity with this name will be used",
            type=str,
        )


class FreezeCommandParser(DaveArgumentParser):
    def __init__(self):
        super().__init__("freeze")
        self.add_argument(
            "VARIABLE_ID",
            help="Name/ID of the variable to freeze. "
            "When providing a conflicting name, the first entity with this name will be used",
            type=str,
        )


class ConcatCommandParser(DaveArgumentParser):
    def __init__(self):
        super().__init__("concat")
        self.add_argument(
            "VARIABLE_ID",
            help="Name/ID of the variable to concatenate. "
            "When providing a conflicting name, the first entity with this name will be used",
            type=str,
        )


class HelpCommandParser(DaveArgumentParser):
    def __init__(self):
        super().__init__("help")
        self.add_argument(
            "SUBCOMMAND",
            nargs="?",
            choices=["show", "delete", "concat", "freeze", "inspect"],
            type=str,
        )
