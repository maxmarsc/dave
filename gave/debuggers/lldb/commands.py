import lldb
import shlex

from ...process import GaveProcess
from ...container_factory import ContainerFactory, ContainerError
from .value import LldbValue


def exit_handler(event):
    if GaveProcess().is_alive():
        # pass
        GaveProcess().should_stop()
        GaveProcess().join()


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
            if GaveProcess().is_alive():
                GaveProcess().gdb_update_callback()
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
        args = shlex.split(command)
        result.AppendMessage(f"{args}")

        if len(args) < 1 or len(args) > 2:
            result.SetError("Usage: gave show <variable> [dim1[,dim2]]")
            return

        varname = args[0]
        dims = [int(val) for val in args[1].split(",")] if len(args) > 1 else []

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
            print(f"Built {type(container)}")
        except (ContainerError, TypeError) as e:
            result.SetError(e.args[0])
            return

        if not GaveProcess().is_alive():
            GaveProcess().start()
        GaveProcess().add_to_model(container)

    def get_short_help(self):
        return "Usage: gave show <variable> [dim1[,dim2]]"
        # this call should return the short help text for this command[1]

    def get_repeat_command(self, command):
        return ""
