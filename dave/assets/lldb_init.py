import lldb  # type: ignore
import logging

try:
    from dave.debuggers.lldb import (
        ShowCommand,
        DeleteCommand,
        FreezeCommand,
        ConcatCommand,
        StopHook,
        LLDBEventHandler,
    )
    from dave import Logger

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

        Logger().get().info("[dave] Successfully loaded")

except ModuleNotFoundError:
    import os, sys

    LOGLEVEL = os.environ.get("DAVE_LOGLEVEL", "INFO").upper()
    logging.basicConfig(level=LOGLEVEL, format="%(levelname)s: %(message)s")
    logging.warning("[dave] module not found. Commands will not be available")
    logging.debug(f"sys.path : {sys.path}")
