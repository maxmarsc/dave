from dave.common.logger import Logger
import dave.common.server_type as st

st.SERVER_TYPE = st.ServerType.GDB

from ...languages import *
from .commands import GdbCommand, exit_handler, stop_handler, frame_checker


import gdb  # type: ignore
import logging
import os

GdbCommand()
gdb.events.exited.connect(exit_handler)
gdb.events.stop.connect(stop_handler)
gdb.events.before_prompt.connect(frame_checker)

Logger().get().info("[dave] Successfully loaded")
