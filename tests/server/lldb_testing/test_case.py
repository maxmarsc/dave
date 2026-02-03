from __future__ import annotations
from pathlib import Path
import lldb

from common import TestCaseBase
from common.debugger import stdout_silence
from lldb_testing.debugger import LldbDebugger


class LldbTestCase(TestCaseBase):
    # We maintain the abstraction as a singleton per class/session
    __DEBUGGER = LldbDebugger()

    @staticmethod
    def debugger():
        return LldbTestCase.__DEBUGGER

    def setUp(self):
        self._check_for_binary()

        # Load the binary into LLDB
        self.__sbdebugger: lldb.SBDebugger = lldb.debugger
        target: lldb.SBTarget = self.__sbdebugger.CreateTarget(
            str(self.BINARY.resolve())
        )
        if not target.IsValid():
            self.fail(f"Failed to create LLDB target for {self.BINARY}")

        # Set the debugger abstraction to use the loaded target
        self.debugger().set(target)

        # Reset the MockClient
        from mocked import MockClient

        MockClient().reset()

    def tearDown(self):
        target: lldb.SBTarget = self.__sbdebugger.GetSelectedTarget()
        if target.IsValid():
            with stdout_silence():
                # Kill the process if still running
                process: lldb.SBProcess = target.GetProcess()
                if process.IsValid() and process.GetState() != lldb.eStateExited:
                    process.Kill()

                # Delete the target, it should remove its breakpoints automatically
                self.__sbdebugger.DeleteTarget(target)

        # Unset the debugger abstraction
        self.debugger().unset()
