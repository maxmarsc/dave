import lldb
import shlex

from ...process import GaveProcess
from ...container_factory import ContainerFactory, ContainerError
from .value import LldbValue
import threading
import time
import weakref


class StopHook:
    def __init__(self, target: lldb.SBTarget, extra_args: lldb.SBStructuredData, _):
        pass

    def handle_stop(self, exe_ctx: lldb.SBExecutionContext, stream: lldb.SBStream):
        # Check if the stop reason is a breakpoint
        if (
            exe_ctx.GetProcess().GetSelectedThread().GetStopReason()
            == lldb.eStopReasonBreakpoint
        ):
            if GaveProcess().is_alive():
                GaveProcess().dbgr_update_callback()
        return True


class LLDBEventHandler:
    def __init__(self, debugger: lldb.SBDebugger):
        self.__debugger = debugger
        self.__listener = lldb.SBListener("dave_process_listener")
        self.attached = False

        # Start listening thread
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
                | lldb.SBProcess.eBroadcastBitInterrupt,
            )
            self.attached = True

    def __close_process(self):
        if GaveProcess().is_alive():
            GaveProcess().should_stop()
            GaveProcess().join()

    def __event_loop(self):
        while True:
            if not self.attached:
                self.__try_to_attach_to_process()
            if GaveProcess().is_alive():
                # Signal we're alive
                GaveProcess().live_signal()

                event = lldb.SBEvent()
                if self.__listener.WaitForEvent(0, event):
                    if lldb.SBProcess.EventIsProcessEvent(event):
                        if (
                            lldb.SBProcess.GetStateFromEvent(event) == lldb.eStateExited
                            or event.GetType() == lldb.SBProcess.eBroadcastBitInterrupt
                        ):
                            self.__close_process()
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
        result.AppendMessage(f"{args}")

        if len(args) < 1 or len(args) > 2:
            result.SetError("Usage: gave show <variable> [dim1[,dim2]]")
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

        var = frame.FindVariable(varname)  # type: lldb.SBValue
        if not var.IsValid():
            result.SetError(f"Variable '{varname}' not found.")
            return
        lldb_value = LldbValue(var)
        typename = lldb_value.typename()
        try:
            container = ContainerFactory().build(lldb_value, typename, varname, dims)
            print(f"Built {varname} : {container.id}")
        except (ContainerError, TypeError) as e:
            result.SetError(e.args[0])
            return

        if not GaveProcess().is_alive():
            GaveProcess().start(True)
        GaveProcess().add_to_model(container)

    def get_short_help(self):
        return "Usage: gave show VARIABLE [DIM1[,DIM2]]"
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
            result.SetError("Usage: gave delete VARIABLE|CONTAINER_ID")
            return

        # Check for running process
        if not exe_ctx.GetProcess().IsValid():
            result.SetError("No processus detected")
            return

        # Check for running dave
        if not GaveProcess().is_alive():
            result.SetError("Dave is not started")
            return

        if not GaveProcess().delete_container(args[0]):
            result.SetError(f"{args[0]} is not a valid name or container id")

    def get_short_help(self):
        return "Usage: gave delete VARIABLE|CONTAINER_ID"

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
            result.SetError("Usage: gave freeze VARIABLE|CONTAINER_ID")
            return

        # Check for running process
        if not exe_ctx.GetProcess().IsValid():
            result.SetError("No processus detected")
            return

        # Check for running dave
        if not GaveProcess().is_alive():
            result.SetError("Dave is not started")
            return

        if not GaveProcess().freeze_container(args[0]):
            result.SetError(f"{args[0]} is not a valid name or container id")

    def get_short_help(self):
        return "Usage: gave delete VARIABLE|CONTAINER_ID"

    def get_repeat_command(self, command):
        return ""
