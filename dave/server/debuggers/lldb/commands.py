import lldb
import shlex

from ...process import DaveProcess
from ...container_factory import ContainerFactory, ContainerError
from dave.common.logger import Logger
from .value import LldbValue
import threading
import time


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
        Logger().get().debug("Creating lldb.SBListener")
        self.__listener = lldb.SBListener("lldb_listener")
        self.attached = False
        self.__last_frame = None

        # Start listening thread
        Logger().get().debug("Creating EventHandler thread")
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
        pass

    def __call__(
        self,
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject,
    ):
        args = shlex.split(command)

        if len(args) < 1 or len(args) > 2:
            result.SetError("Usage: dave show <variable> [dim1[,dim2]]")
            return

        varname = args[0]
        dims = [int(val) for val in args[1].split(",")] if len(args) > 1 else []

        # Check for running process
        if not exe_ctx.GetProcess().IsValid():
            result.SetError("No processus detected")
            return

        # Get the frame
        frame = exe_ctx.GetFrame()  # type: lldb.SBFrame
        if not frame:
            result.SetError("No valid frame to evaluate variable.")
            return

        var = LldbValue.find_variable_robust(varname, frame)
        if not var.IsValid():
            result.SetError(f"Variable '{varname}' not found.")
            return

        lldb_value = LldbValue(var, varname)
        typename = lldb_value.typename()
        try:
            container = ContainerFactory().build(lldb_value, typename, varname, dims)
            Logger().get().info(f"Added {varname} : {container.id}")
        except (ContainerError, TypeError) as e:
            result.SetError(e.args[0])
            return

        if not DaveProcess().is_alive():
            DaveProcess().start()
        DaveProcess().add_to_model(container)

    def get_short_help(self):
        return "Usage: dave show VARIABLE [DIM1[,DIM2]]"
        # this call should return the short help text for this command[1]

    def get_repeat_command(self, command):
        return ""


class DeleteCommand:
    def __init__(self, debugger: lldb.SBDebugger, internal_dict):
        pass

    def __call__(
        self,
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject,
    ):
        args = shlex.split(command)
        result.AppendMessage(f"{args}")

        if len(args) != 1:
            result.SetError("Usage: dave delete VARIABLE|CONTAINER_ID")
            return

        # Check for running process
        if not exe_ctx.GetProcess().IsValid():
            result.SetError("No processus detected")
            return

        # Check for running dave
        if not DaveProcess().is_alive():
            result.SetError("Dave is not started")
            return

        if not DaveProcess().delete_container(args[0]):
            result.SetError(f"{args[0]} is not a valid name or container id")

    def get_short_help(self):
        return "Usage: dave delete VARIABLE|CONTAINER_ID"

    def get_repeat_command(self, command):
        return ""


class FreezeCommand:
    def __init__(self, debugger: lldb.SBDebugger, internal_dict):
        pass

    def __call__(
        self,
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject,
    ):
        args = shlex.split(command)
        result.AppendMessage(f"{args}")

        if len(args) != 1:
            result.SetError("Usage: dave freeze VARIABLE|CONTAINER_ID")
            return

        # Check for running process
        if not exe_ctx.GetProcess().IsValid():
            result.SetError("No processus detected")
            return

        # Check for running dave
        if not DaveProcess().is_alive():
            result.SetError("Dave is not started")
            return

        if not DaveProcess().freeze_container(args[0]):
            result.SetError(f"{args[0]} is not a valid name or container id")

    def get_short_help(self):
        return "Usage: dave delete VARIABLE|CONTAINER_ID"

    def get_repeat_command(self, command):
        return ""


class ConcatCommand:
    def __init__(self, debugger: lldb.SBDebugger, internal_dict):
        pass

    def __call__(
        self,
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject,
    ):
        args = shlex.split(command)
        result.AppendMessage(f"{args}")

        if len(args) != 1:
            result.SetError("Usage: dave concat VARIABLE|CONTAINER_ID")
            return

        # Check for running process
        if not exe_ctx.GetProcess().IsValid():
            result.SetError("No processus detected")
            return

        # Check for running dave
        if not DaveProcess().is_alive():
            result.SetError("Dave is not started")
            return

        if not DaveProcess().concat_container(args[0]):
            result.SetError(f"{args[0]} is not a valid name or container id")

    def get_short_help(self):
        return "Usage: dave delete VARIABLE|CONTAINER_ID"

    def get_repeat_command(self, command):
        return ""
