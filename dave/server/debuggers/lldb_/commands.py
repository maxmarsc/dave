from typing import List
import lldb
import shlex

from ...process import DaveProcess
from ...entity_factory import EntityFactory, EntityBuildError
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
from dave.common.logger import Logger
from .value import LldbValue
import threading
import time
import os


def xcode_detected() -> bool:
    return (
        os.environ.get("DYLD_FRAMEWORK_PATH", None)
        == "/Applications/Xcode.app/Contents/SharedFrameworks"
    )


class StopHook:
    def __init__(self, target: lldb.SBTarget, extra_args: lldb.SBStructuredData, _):
        pass

    def handle_stop(self, exe_ctx: lldb.SBExecutionContext, stream: lldb.SBStream):
        stop_reason = exe_ctx.GetProcess().GetSelectedThread().GetStopReason()

        # Check if the stop reason is a breakpoint or step-over
        if stop_reason in (lldb.eStopReasonBreakpoint, lldb.eStopReasonPlanComplete):
            if DaveProcess().is_alive():
                DaveProcess().dbgr_update_callback()
        return True


class LLDBEventHandler:
    def __init__(self, debugger: lldb.SBDebugger):
        self.__debugger = debugger
        Logger().debug("Creating lldb.SBListener")
        self.__listener = lldb.SBListener("lldb_listener")
        self.attached = False
        self.__last_frame = None

        # Start listening thread
        Logger().debug("Creating EventHandler thread")
        self.__thread = threading.Thread(target=self.__event_loop)
        self.__thread.start()

    def __try_to_attach_to_process(self):
        process = (
            self.__debugger.GetSelectedTarget().GetProcess()
        )  # type: lldb.SBProcess
        if process.is_alive:
            process.broadcaster.AddListener(
                self.__listener,
                lldb.SBProcess.eBroadcastBitStateChanged
                | lldb.SBProcess.eBroadcastBitInterrupt
                | lldb.SBProcess.eBroadcastBitStateChanged,
            )

            # Get the broadcaster class name for SBThread
            thread_broadcaster_class = lldb.SBThread.GetBroadcasterClassName()

            # Start listening for thread events
            self.__listener.StartListeningForEventClass(
                self.__debugger,
                thread_broadcaster_class,
                lldb.SBThread.eBroadcastBitSelectedFrameChanged
                | lldb.SBThread.eBroadcastBitStackChanged,
            )

            self.attached = True

    def __close_process(self):
        if DaveProcess().is_alive():
            DaveProcess().should_stop()
            DaveProcess().join()

    def __check_frame_change(self):
        current_frame = (
            self.__debugger.GetSelectedTarget()
            .GetProcess()
            .GetSelectedThread()
            .GetSelectedFrame()
        )
        if DaveProcess().is_alive() and current_frame != self.__last_frame:
            Logger().debug("Frame change detected, updating")
            DaveProcess().dbgr_update_callback()
            self.__last_frame = current_frame

    def __event_loop(self):
        while True:
            if not self.attached:
                self.__try_to_attach_to_process()

            if DaveProcess().is_alive():

                event = lldb.SBEvent()
                if self.__listener.WaitForEvent(0, event):
                    if lldb.SBProcess.EventIsProcessEvent(event):
                        if (
                            lldb.SBProcess.GetStateFromEvent(event) == lldb.eStateExited
                            or event.GetType() == lldb.SBProcess.eBroadcastBitInterrupt
                        ):
                            self.__close_process()
                    elif lldb.SBThread.EventIsThreadEvent(event):
                        self.__check_frame_change()
            time.sleep(0.02)


class ShowCommand:
    def __init__(self, debugger: lldb.SBDebugger, internal_dict):
        self.__parser = ShowCommandParser()

    def __call__(
        self,
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject,
    ):
        args = shlex.split(command)
        try:
            parsed = self.__parser.parse_args(args)
        except ParsingError as e:
            result.SetError(self.__parser.usage_property)
            return
        except HelpException as e:
            return

        if len(parsed.dims) > 2:
            result.SetError("--dims supports up to two dimensions")
            return

        # Check for running process
        if not exe_ctx.GetProcess().IsValid():
            result.SetError("No processus detected")
            return

        # Get the frame
        frame = exe_ctx.GetFrame()  # type: lldb.SBFrame
        if not frame:
            result.SetError("No valid frame to evaluate variable.")
            return

        if parsed.VARIABLE:
            vars: List[LldbValue] = [
                LldbValue.find_variable(parsed.VARIABLE, frame),
            ]
            if vars[0] is None:
                result.SetError(f"Variable '{parsed.VARIABLE}' not found.")
                return
        else:
            vars: List[LldbValue] = LldbValue.find_all_variables()

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
                    result.SetError(e.args[0])
                    return
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
            DaveProcess().add_to_model(new_entities)

    def get_short_help(self):
        return self.__parser.usage_property
        # this call should return the short help text for this command[1]

    def get_repeat_command(self, command):
        return ""


class InspectCommand:
    def __init__(self, debugger: lldb.SBDebugger, internal_dict):
        self.__parser = InspectCommandParser()

    def __call__(
        self,
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject,
    ):
        try:
            args = self.__parser.parse_args(shlex.split(command))
        except ParsingError as e:
            result.SetError(self.__parser.usage_property)
            return
        except HelpException as e:
            return

        # Check for running process
        if not exe_ctx.GetProcess().IsValid():
            result.SetError("No processus detected")
            return

        # Get the frame
        frame = exe_ctx.GetFrame()  # type: lldb.SBFrame
        if not frame:
            result.SetError("No valid frame to evaluate variable.")
            return

        lldb_value = LldbValue.find_variable(args.VARIABLE, frame)
        if lldb_value is None:
            result.SetError(f"Variable '{args.VARIABLE}' not found.")
            return

        Logger().info(lldb_value.typename())

    def get_short_help(self):
        return self.__parser.usage_property


class HelpCommand:
    def __init__(self, debugger: lldb.SBDebugger, internal_dict):
        self.__parser = HelpCommandParser()

    def __call__(
        self,
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject,
    ):
        try:
            args = self.__parser.parse_args(shlex.split(command))
        except ParsingError as e:
            result.SetError(self.__parser.usage_property)
            return
        except HelpException as e:
            return

        match args.SUBCOMMAND:
            case None:
                # Get the command interpreter
                interpreter = debugger.GetCommandInterpreter()

                # Create an output object to capture the result
                result = lldb.SBCommandReturnObject()

                # Execute the command
                interpreter.HandleCommand("help dave", result)

                # Print the command output
                if result.Succeeded():
                    print(result.GetOutput())
                else:
                    print("Command failed:", result.GetError())
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
                result.SetError("Uh-Oh, something went wrong")

    def get_short_help(self):
        return self.__parser.usage_property


class DeleteCommand:
    def __init__(self, debugger: lldb.SBDebugger, internal_dict):
        self.__parser = DeleteCommandParser()

    def __call__(
        self,
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject,
    ):
        try:
            args = self.__parser.parse_args(shlex.split(command))
        except ParsingError as e:
            result.SetError(self.__parser.usage_property)
            return
        except HelpException as e:
            return

        # Check for running process
        if not exe_ctx.GetProcess().IsValid():
            result.SetError("No processus detected")
            return

        # Check for running dave
        if not DaveProcess().is_alive():
            result.SetError("Dave is not started")
            return

        if not DaveProcess().delete(args.VARIABLE_ID):
            result.SetError(f"{args.VARIABLE_ID} is not a valid name or container id")

    def get_short_help(self):
        return self.__parser.usage_property

    def get_repeat_command(self, command):
        return ""


class FreezeCommand:
    def __init__(self, debugger: lldb.SBDebugger, internal_dict):
        self.__parser = FreezeCommandParser()

    def __call__(
        self,
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject,
    ):
        try:
            args = self.__parser.parse_args(shlex.split(command))
        except ParsingError as e:
            result.SetError(self.__parser.usage_property)
            return
        except HelpException as e:
            return

        # Check for running process
        if not exe_ctx.GetProcess().IsValid():
            result.SetError("No processus detected")
            return

        # Check for running dave
        if not DaveProcess().is_alive():
            result.SetError("Dave is not started")
            return

        if not DaveProcess().freeze(args.VARIABLE_ID):
            result.SetError(f"{args.VARIABLE_ID} is not a valid name or container id")

    def get_short_help(self):
        return self.__parser.usage_property

    def get_repeat_command(self, command):
        return ""


class ConcatCommand:
    def __init__(self, debugger: lldb.SBDebugger, internal_dict):
        self.__parser = ConcatCommandParser()

    def __call__(
        self,
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject,
    ):
        try:
            args = self.__parser.parse_args(shlex.split(command))
        except ParsingError as e:
            result.SetError(self.__parser.usage_property)
            return
        except HelpException as e:
            return

        # Check for running process
        if not exe_ctx.GetProcess().IsValid():
            result.SetError("No processus detected")
            return

        # Check for running dave
        if not DaveProcess().is_alive():
            result.SetError("Dave is not started")
            return

        if not DaveProcess().concat(args.VARIABLE_ID):
            result.SetError(f"{args.VARIABLE_ID} is not a valid name or container id")

    def get_short_help(self):
        return self.__parser.usage_property

    def get_repeat_command(self, command):
        return ""
