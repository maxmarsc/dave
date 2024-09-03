from ...languages.c_cpp import *
from .commands import GdbCommand, exit_handler, stop_handler, frame_checker

import gdb  # type: ignore

GdbCommand()
gdb.events.exited.connect(exit_handler)
gdb.events.stop.connect(stop_handler)
gdb.events.before_prompt.connect(frame_checker)

print("[dave] Successfully loaded")
