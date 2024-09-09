from ...languages.c_cpp import *
from ...logger import Logger
from .commands import GdbCommand, exit_handler, stop_handler, frame_checker

import gdb  # type: ignore
import logging
import os

GdbCommand()
gdb.events.exited.connect(exit_handler)
gdb.events.stop.connect(stop_handler)
gdb.events.before_prompt.connect(frame_checker)

Logger().get().info("[dave] Successfully loaded")
