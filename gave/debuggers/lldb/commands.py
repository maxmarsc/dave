import lldb
import optparse
import shlex

from ...process import GaveProcess


class StopHook:
    def __init__(self, target: lldb.SBTarget, extra_args: lldb.SBStructuredData, _):
        pass

    def handle_stop(self, exe_ctx: lldb.SBExecutionContext, stream: lldb.SBStream):
        stream.Print(
            f"Stop event detected {exe_ctx.GetProcess().GetSelectedThread().GetStopReason()}\n"
        )
        # Check if the stop reason is a breakpoint
        if (
            exe_ctx.GetProcess().GetSelectedThread().GetStopReason()
            == lldb.eStopReasonBreakpoint
        ):
            stream.Print("Breakpoint detected\n")
        return True


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
        # this is the actual bulk of the command, akin to Python command functions
        pass

    def get_short_help(self):
        return "Usage: gave show <variable> [dim1[,dim2]]"
        # this call should return the short help text for this command[1]

    def get_repeat_command(self, command):
        return ""
