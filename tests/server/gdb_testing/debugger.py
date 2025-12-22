from collections import deque
from typing import List
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

    def set_breakpoints_at_tags(self, function: str, tags: List[int]):
        unparsed, parsed = gdb.decode_line(function)
        if unparsed:
            raise RuntimeError(f"Could not find function {function}")

        tags.sort()
        loc: gdb.Symtab_and_line = parsed[0]
        filename = loc.symtab.fullname()

        tags_lines = self._find_tags(filename, function, loc.line, tags)
        for tag_line in tags_lines:
            self.set_breakpoint(tag_line)

    def run(_):
        with gdb_stdout_silence():
            gdb.execute("run", to_string=True)

    def continue_(_):
        with gdb_stdout_silence():
            gdb.execute("continue", to_string=True)

    def execute(_, command) -> str:
        return gdb.execute(command, to_string=True)
