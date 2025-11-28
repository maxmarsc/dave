from dave.common.logger import Logger
import dave.common.server_type as st

st.SERVER_TYPE = st.ServerType.GDB

from ...languages import *
from .commands import GdbCommand, exit_handler, stop_handler
from .formatters import dave_printer


import gdb  # type: ignore
import logging
import os

GdbCommand()
gdb.events.exited.connect(exit_handler)
gdb.events.stop.connect(stop_handler)
gdb.pretty_printers.append(dave_printer)

gdb.write("INFO : [dave] Successfully loaded\n")

# If the flag is set, wait for the python debugger to connect
if os.environ.get("DAVE_DEBUG_SERVER") == "1":
    try:
        import debugpy

        gdb.write("Waiting for debugger to attach on port 5678...")
        debugpy.listen(("localhost", 5678))
        debugpy.wait_for_client()
        gdb.write("Debugger attached! Continuing...")
    except ImportError:
        gdb.write("Error: 'debugpy' not found. Cannot attach debugger.")
