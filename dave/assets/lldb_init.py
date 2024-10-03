import lldb  # type: ignore
import logging
import subprocess
import sys
import os

# Update LLDB's Python paths with the `sys.path` values of the local
from pathlib import Path

try:
    DAVE_VENV_PATH = Path(os.environ["DAVE_VENV_FOLDER"]) / "bin/activate"
except KeyError:
    DAVE_VENV_PATH = Path.home() / ".dave/venv/bin/activate"

# Execute a Python using the user's shell and pull out the sys.path (for site-packages)
if DAVE_VENV_PATH.is_file():
    paths = (
        subprocess.check_output(
            '. {};python -c "import os,sys;print(os.linesep.join(sys.path).strip())"'.format(
                DAVE_VENV_PATH
            ),
            shell=True,
        )
        .decode("utf-8")
        .split()
    )
    # Delete duplicates and update the search list with dave venv
    sys.path = list(dict.fromkeys(sys.path + paths))

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
