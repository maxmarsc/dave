import gdb  # type: ignore

from common.debugger import DebuggerAbstraction

import os
import sys
from contextlib import contextmanager


@contextmanager
def gdb_stdout_silence():
    # Save a copy of the actual terminal output (FD 1)
    stdout_fd = 1
    saved_stdout_fd = os.dup(stdout_fd)

    try:
        # Redirect FD 1 to /dev/null
        # This affects the ENTIRE process, including GDB's C code
        with open(os.devnull, "w") as devnull:
            os.dup2(devnull.fileno(), stdout_fd)
            yield
    finally:
        # Restore the original terminal output to FD 1
        os.dup2(saved_stdout_fd, stdout_fd)
        os.close(saved_stdout_fd)


class GdbDebugger(DebuggerAbstraction):
    def set_breakpoint(_, location: str):
        gdb.execute(f"b {location}", to_string=True)

    def run(_):
        # gdb.execute("set logging enabled on", to_string=True, from_tty=True)

        # try:
        with gdb_stdout_silence():
            gdb.execute("run", to_string=True)
        # finally:
        # gdb.execute("set logging enabled off", to_string=True, from_tty=True)

    def con(_):
        # gdb.execute("set logging enabled on", to_string=True, from_tty=True)

        # try:
        with gdb_stdout_silence():
            gdb.execute("continue", to_string=True)
        # finally:
        # gdb.execute("set logging enabled off", to_string=True, from_tty=True)

    def execute(_, command) -> str:
        return gdb.execute(command, to_string=True)
