from dave.common.logger import Logger
import dave.common.server_type as st

st.SERVER_TYPE = st.ServerType.GDB

from ...languages import *
from .commands import GdbCommand, exit_handler, stop_handler


import gdb  # type: ignore
import logging
import os

GdbCommand()
gdb.events.exited.connect(exit_handler)
gdb.events.stop.connect(stop_handler)

gdb.write("INFO : [dave] Successfully loaded\n")
