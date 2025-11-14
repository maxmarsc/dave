from __future__ import annotations
from argparse import SUPPRESS, Action, ArgumentParser, Namespace, ArgumentError
from abc import ABC, abstractmethod
import types
import traceback

from dave.common.logger import Logger
from typing import Union, override


class ParsingError(Exception):
    pass


class HelpException(Exception):
    pass


class NonExitingHelpAction(Action):
    def __init__(self, option_strings, dest=SUPPRESS, default=SUPPRESS, help=None):
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()
        raise HelpException()


class DaveArgumentParser(ArgumentParser, ABC):
    """
    Custom workaround class, see https://github.com/python/cpython/issues/103498
    """

    def __init__(self, subprog: str, **kwargs):
        kwargs["add_help"] = False
        super().__init__(prog=f"dave {subprog}", **kwargs)

        self.add_argument(
            "-h",
            "--help",
            action=NonExitingHelpAction,
            help="show this help message and returns",
        )

    @property
    def subprog(self) -> str:
        return self.prog.split()[1]

    @property
    def usage_property(self) -> str:
        # Delete the \n at the end
        return self.format_usage()[:-1]

    @override
    def error(self, message):
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
