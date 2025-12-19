from __future__ import annotations
from pathlib import Path
import gdb  # type: ignore

from common import TestCaseBase
from gdb_testing.debugger import GdbDebugger


class GdbTestCase(TestCaseBase):
    __DEBUGGER = GdbDebugger()

    @staticmethod
    def debugger():
        return GdbTestCase.__DEBUGGER

    def setUp(self):
        if not self.BINARY or not self.BINARY_HASH:
            self.fail("Missing BINARY or BINARY_HASH class attributes")

        # TODO: check hash matches
        self.assertTrue(self.BINARY.is_file(), f"Binary {self.BINARY} does not exist")

        # Check for any previous running threads
        if gdb.selected_inferior().threads():
            self.fail("There are leftover running threads from a previous test")

        # Load the binary
        gdb.execute(f"file {self.BINARY}", to_string=True)

    def tearDown(self):
        # Kill any leftover running threads
        if gdb.selected_inferior().threads():
            gdb.execute("kill", to_string=True)

        # Use the 'file' command without arguments to unload the binary
        gdb.execute("set confirm off", to_string=True)
        try:
            gdb.execute("file", to_string=True)
        except Exception:
            # GDB sometimes throws an exception if no file was loaded,
            # or if the command returns nothing interesting. We can ignore this.
            pass
        gdb.execute("set confirm on", to_string=True)

        # Delete all remaining breakpoints
        gdb.execute("delete", to_string=True)
