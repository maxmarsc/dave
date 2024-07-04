from ...languages.c_cpp import *
from .commands import GdbCommand, exit_handler, stop_handler

import gdb  # type: ignore

GdbCommand()
gdb.events.exited.connect(exit_handler)
gdb.events.stop.connect(stop_handler)
