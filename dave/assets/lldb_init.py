import lldb  # type: ignore

try:
    from dave.debuggers.lldb import (
        ShowCommand,
        DeleteCommand,
        FreezeCommand,
        ConcatCommand,
        StopHook,
        LLDBEventHandler,
    )

    def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict):
        # Register dave commands
        debugger.HandleCommand(
            'command container add -h "A container for my dave commands" dave'
        )
        # debugger.HandleCommand(f"command script add -f {__name__}.ShowCommand dave show")
        debugger.HandleCommand(
            f"command script add -c {__name__}.ShowCommand dave show"
        )
        debugger.HandleCommand(
            f"command script add -c {__name__}.DeleteCommand dave delete"
        )
        debugger.HandleCommand(
            f"command script add -c {__name__}.FreezeCommand dave freeze"
        )
        debugger.HandleCommand(
            f"command script add -c {__name__}.ConcatCommand dave concat"
        )

        # Register stop event hook
        debugger.HandleCommand(f"target stop-hook add -P {__name__}.StopHook")

        # Event handler to handle process stop
        event_handler = LLDBEventHandler(debugger)

        print("[dave] Successfully loaded")

except ModuleNotFoundError:
    print("[dave] module not found. Commands will not be available")
