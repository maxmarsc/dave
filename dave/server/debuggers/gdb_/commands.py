from typing import List
import gdb  # type: ignore
import gdb.types  # type: ignore

import threading
import time

from dave.common.singleton import SingletonMeta
from dave.server.process import DaveProcess
from dave.server.debuggers.command_parsers import (
    HelpException,
    ParsingError,
    ShowCommandParser,
    DeleteCommandParser,
    InspectCommandParser,
    FreezeCommandParser,
    ConcatCommandParser,
    HelpCommandParser,
)
from dave.server.entity_factory import EntityFactory, EntityBuildError
from dave.common.logger import Logger

from .value import GdbValue

# Needed for f-string formatting of GdbCommand class
SHOW_PARSER = ShowCommandParser()
DELETE_PARSER = DeleteCommandParser()
INSPECT_PARSER = InspectCommandParser()
FREEZE_PARSER = FreezeCommandParser()
CONCAT_PARSER = ConcatCommandParser()
HELP_PARSER = HelpCommandParser()


def exit_handler(event):
    if FrameCheckerThread().is_alive():
        FrameCheckerThread().should_stop()
        FrameCheckerThread().join()

    if DaveProcess().is_alive():
        DaveProcess().should_stop()
        DaveProcess().join()


def stop_handler(event: gdb.StopEvent):
    if DaveProcess().is_alive():
        DaveProcess().dbgr_update_callback()


class FrameCheckerThread(metaclass=SingletonMeta):
    def __init__(self):
        self.__thread = None  # type: threading.Thread
        self.__should_stop = False
        self.__last_frame = None

    def start(self):
        if self.__thread is not None and self.__thread.is_alive():
            raise RuntimeError("Dave frame checker was already started")
        self.__thread = threading.Thread(target=self.routine, name="dave frame checker")
        self.__thread.start()

    def join(self):
        if self.__thread is not None and self.__thread.is_alive():
            self.__thread.join()
            self.__thread = None

    def routine(self):
        while not self.__should_stop and DaveProcess().is_alive():
            gdb.post_event(self.check_frame)
            time.sleep(0.1)

    def check_frame(self):
        if self.__should_stop:
            return
        try:
            current_frame = gdb.selected_frame()
            if current_frame != self.__last_frame and DaveProcess().is_alive():
                if self.__last_frame is not None:
                    DaveProcess().dbgr_update_callback()
                self.__last_frame = current_frame
                Logger().debug("Frame change detected, updating")
        except gdb.error:
            pass

    def should_stop(self):
        self.__should_stop = True

    def is_alive(self) -> bool:
        if self.__thread is not None:
            return self.__thread.is_alive()
        return False


class GdbCommand(gdb.Command):
    # fmt: off
    __doc__ = f"""
DAVE subcommands to communicate with the dave gui

To have more information check the user guide : https://github.com/maxmarsc/dave/blob/main/USER_GUIDE.md

The following subcommands are supported:

    concat  -- {CONCAT_PARSER.usage_property}
    delete  -- {DELETE_PARSER.usage_property}
    freeze  -- {FREEZE_PARSER.usage_property}
    help    -- {HELP_PARSER.usage_property}
    inspect -- {INSPECT_PARSER.usage_property}
    show    -- {SHOW_PARSER.usage_property}
    """
    # fmt: on

    def __init__(self):
        super(GdbCommand, self).__init__("dave", gdb.COMMAND_USER, gdb.COMPLETE_SYMBOL)

    @staticmethod
    def __check_for_running_inferior() -> bool:
        """Return True if the current inferior is actually started"""
        if gdb.selected_inferior().pid <= 0:
            return False
        else:
            return True

    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        if len(args) < 1:
            raise gdb.GdbError(self.__doc__)

        if not GdbCommand.__check_for_running_inferior() and args[0] != "help":
            raise gdb.GdbError("No processus detected")

        subcommand = args[0]
        match subcommand:
            case INSPECT_PARSER.subprog:
                self.__inspect(args[1:])
            case SHOW_PARSER.subprog:
                self.__show(args[1:])
            case DELETE_PARSER.subprog:
                self.__delete(args[1:])
            case FREEZE_PARSER.subprog:
                self.__freeze(args[1:])
            case CONCAT_PARSER.subprog:
                self.__concat(args[1:])
            case HELP_PARSER.subprog:
                self.__help(args[1:])
            case _:
                raise gdb.GdbError(f"Unknown subcommand '{subcommand}'")

    def __show(self, args):
        try:
            parsed = SHOW_PARSER.parse_args(args)
        except ParsingError as e:
            message = f"{e}\n{SHOW_PARSER.usage_property}"
            raise gdb.GdbError(message)
        except HelpException as e:
            return

        if len(parsed.dims) > 2:
            raise gdb.GdbError("--dims supports up to two dimensions")

        if parsed.VARIABLE:
            # The user gave a variable name
            vars: List[GdbValue] = [
                GdbValue.find_variable(parsed.VARIABLE),
            ]
            if vars[0] is None:
                raise gdb.GdbError(f"Variable '{parsed.VARIABLE}' not found.")
        else:
            # The user gave no name, we will try to add every compatible variable
            vars: List[GdbValue] = GdbValue.find_all_variables()

        skipped = []
        new_entities = []
        for var in vars:
            # Check for uninitialized references
            if var.address() == 0:
                Logger().info(f"Skipping {var.varname()} because its address is 0x0")
                skipped.append(var.varname())
                continue

            try:
                entity = EntityFactory().build(
                    var, var.typename(), var.varname(), parsed.dims
                )
                Logger().info(f"Added {var.varname()} with ID {entity.id}")
                new_entities.append(entity)
            except (EntityBuildError, TypeError) as e:
                if parsed.VARIABLE:
                    raise gdb.GdbError(e.args[0])
                else:
                    Logger().debug(f"Failed to build {var.varname()} with {e}")
                    skipped.append(var.varname())
        if skipped:
            skipped_str = str(skipped)[1:-1]
            skipped_str = skipped_str.replace("'", "")
            Logger().info(f"Skipped the following variables : {skipped_str}")

        if new_entities:
            if not DaveProcess().is_alive():
                DaveProcess().start()
                FrameCheckerThread().start()
            DaveProcess().add_to_model(new_entities)

    def __delete(self, args):
        try:
            parsed = DELETE_PARSER.parse_args(args)
        except ParsingError as e:
            message = f"{e}\n{DELETE_PARSER.usage_property}"
            raise gdb.GdbError(message)
        except HelpException as e:
            return

        if not DaveProcess().is_alive():
            raise gdb.GdbError("Dave is not started")

        if not DaveProcess().delete(parsed.VARIABLE_ID):
            raise gdb.GdbError(f"{args[0]} is not a valid entity identifier")

    def __freeze(self, args):
        try:
            parsed = FREEZE_PARSER.parse_args(args)
        except ParsingError as e:
            message = f"{e}\n{FREEZE_PARSER.usage_property}"
            raise gdb.GdbError(message)
        except HelpException as e:
            return

        if not DaveProcess().is_alive():
            raise gdb.GdbError("Dave is not started")

        if not DaveProcess().freeze(parsed.VARIABLE_ID):
            raise gdb.GdbError(
                f"{parsed.VARIABLE_ID} is not a valid name or container id"
            )

    def __concat(self, args):
        try:
            parsed = CONCAT_PARSER.parse_args(args)
        except ParsingError as e:
            message = f"{e}\n{CONCAT_PARSER.usage_property}"
            raise gdb.GdbError(message)
        except HelpException as e:
            return

        if not DaveProcess().is_alive():
            raise gdb.GdbError("Dave is not started")

        if not DaveProcess().concat(parsed.VARIABLE_ID):
            raise gdb.GdbError(
                f"concat command failed. {parsed.VARIABLE_ID} is not a valid "
                "or compatible entity identifier"
            )

    def __inspect(self, args):
        try:
            parsed = INSPECT_PARSER.parse_args(args)
        except ParsingError as e:
            message = f"{e}\n{INSPECT_PARSER.usage_property}"
            raise gdb.GdbError(message)
        except HelpException as e:
            return

        var_name = parsed.VARIABLE
        try:
            var = gdb.parse_and_eval(var_name)
            if var.is_optimized_out:
                print(f"Variable '{var_name}' is optimized out.")
            else:
                print("Type: {}".format(gdb.types.get_basic_type(var.type).name))
        except (gdb.error, RuntimeError) as e:
            print(f"Error accessing variable '{var_name}': {str(e)}")

    def __help(self, args):
        try:
            parsed = HELP_PARSER.parse_args(args)
        except ParsingError as e:
            message = f"{e}\n{INSPECT_PARSER.usage_property}"
            raise gdb.GdbError(message)
        except HelpException as e:
            return

        match parsed.SUBCOMMAND:
            case None:
                print(GdbCommand.__doc__)
            case "show":
                print(ShowCommandParser().format_help()[:-1])
            case "delete":
                print(DeleteCommandParser().format_help()[:-1])
            case "concat":
                print(ConcatCommandParser().format_help()[:-1])
            case "freeze":
                print(FreezeCommandParser().format_help()[:-1])
            case "inspect":
                print(DeleteCommandParser().format_help()[:-1])
            case _:
                raise gdb.GdbError("Uh-Oh, something went wrong")
