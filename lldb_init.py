# import .debuggers.lldb
from gave.debuggers.lldb import ShowCommand, StopHook
import lldb  # type: ignore


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict):
    # Register dave commands
    debugger.HandleCommand(
        'command container add -h "A container for my dave commands" gave'
    )
    # debugger.HandleCommand(f"command script add -f {__name__}.ShowCommand gave show")
    debugger.HandleCommand(f"command script add -c {__name__}.ShowCommand gave show")

    # Register stop event hook
    debugger.HandleCommand(f"target stop-hook add -P {__name__}.StopHook")
