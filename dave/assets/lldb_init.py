import lldb  # type: ignore
import logging
import subprocess
import sys
import os
import re
import site

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
    for path in paths:
        if path not in sys.path:
            site.addsitedir(path)

try:
    import dave.common.server_type as st

    st.SERVER_TYPE = st.ServerType.LLDB

    from dave.server.debuggers.lldb_ import (
        ShowCommand,
        DeleteCommand,
        FreezeCommand,
        ConcatCommand,
        StopHook,
        InspectCommand,
        HelpCommand,
        LLDBEventHandler,
        summary_provider,
        SyntheticChildrenProvider,
    )
    from dave.common.logger import Logger
    from dave.server.entity_factory import EntityFactory

    def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict):
        # Register dave commands
        debugger.HandleCommand(
            'command container add -h "DAVE subcommands to communicate with the dave gui\nTo have more information check the user guide : https://github.com/maxmarsc/dave/blob/main/USER_GUIDE.md" dave'
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
        debugger.HandleCommand(
            f"command script add -c {__name__}.InspectCommand dave inspect"
        )
        debugger.HandleCommand(
            f"command script add -c {__name__}.HelpCommand dave help"
        )

        # Register stop event hook
        debugger.HandleCommand(f"target stop-hook add -P {__name__}.StopHook")

        # Event handler to handle process stop
        event_handler = LLDBEventHandler(debugger)

        # Register pretty printers
        for cls in EntityFactory().get_entities_cls_set():
            if cls.formatter_compatible():
                regex = cls.typename_matcher()
                if isinstance(regex, re.Pattern):
                    # Register summary - lldb does not support non capturing groups
                    stripped_pattern = str(regex.pattern).replace("(?:", "(")
                    debugger.HandleCommand(
                        f'type summary add --expand -x "{stripped_pattern}" -F {__name__}.summary_provider -w dave'
                    )
                    # Register synthetic type
                    debugger.HandleCommand(
                        f'type synthetic add -x "{stripped_pattern}" --python-class {__name__}.SyntheticChildrenProvider -w dave'
                    )
        debugger.HandleCommand("type category enable dave")

        Logger().info("[dave] Successfully loaded")

except ModuleNotFoundError as e:
    import os, sys

    LOGLEVEL = os.environ.get("DAVE_LOGLEVEL", "INFO").upper()
    logging.basicConfig(level=LOGLEVEL, format="%(levelname)s: %(message)s")
    logging.warning("[dave] module not found. Commands will not be available")
    logging.debug(f"failed with {e}")
    logging.debug(f"sys.path : {sys.path}")
