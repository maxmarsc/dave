import lldb  # type: ignore
import logging
import subprocess
import sys

paths = (
    subprocess.check_output(
        'python -c "import os,sys;print(os.linesep.join(sys.path).strip())"', shell=True
    )
    .decode("utf-8")
    .split()
)
# Extend LLDB's Python's search path
sys.path.extend(paths)

try:
    from dave.common.server_type import *
    SERVER_TYPE = ServerType.LLDB
    
    from dave.server.debuggers.lldb import (
        ShowCommand,
        DeleteCommand,
        FreezeCommand,
        ConcatCommand,
        StopHook,
        LLDBEventHandler,
    )
    from dave.common.logger import Logger

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

except ModuleNotFoundError as e:
    import os, sys

    LOGLEVEL = os.environ.get("DAVE_LOGLEVEL", "INFO").upper()
    logging.basicConfig(level=LOGLEVEL, format="%(levelname)s: %(message)s")
    logging.warning("[dave] module not found. Commands will not be available")
    logging.debug(f"failed with {e}")
    logging.debug(f"sys.path : {sys.path}")
