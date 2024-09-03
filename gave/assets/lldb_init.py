import lldb  # type: ignore


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict):
    try:
        from gave.debuggers.lldb import (
            ShowCommand,
            DeleteCommand,
            FreezeCommand,
            ConcatCommand,
            StopHook,
            LLDBEventHandler,
        )
    except ModuleNotFoundError:
        print("[dave] module not found. Commands will not be available")
        return

    # Register dave commands
    debugger.HandleCommand(
        'command container add -h "A container for my dave commands" gave'
    )
    # debugger.HandleCommand(f"command script add -f {__name__}.ShowCommand gave show")
    debugger.HandleCommand(f"command script add -c {__name__}.ShowCommand gave show")
    debugger.HandleCommand(
        f"command script add -c {__name__}.DeleteCommand gave delete"
    )
    debugger.HandleCommand(
        f"command script add -c {__name__}.FreezeCommand gave freeze"
    )
    debugger.HandleCommand(
        f"command script add -c {__name__}.ConcatCommand gave concat"
    )

    # Register stop event hook
    debugger.HandleCommand(f"target stop-hook add -P {__name__}.StopHook")

    # Event handler to handle process stop
    event_handler = LLDBEventHandler(debugger)

    print("[dave] Successfully loaded")
