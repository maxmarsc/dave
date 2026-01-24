from typing import List, Tuple
import struct

from common import TestCaseBase, C_CPP_BUILD_DIR, CommandError
from mocked import MockClient, patch_client_popen

NO_PROCESSUS_DETECTED = CommandError("No processus detected")


class TestContainerPrettyPrinters(TestCaseBase.TYPE):
    BINARY = C_CPP_BUILD_DIR / "custom_tests"
    BINARY_HASH = "hihou"

    @patch_client_popen
    def test_show_no_processus(self, _):
        # No args
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave show")
        self.assertExceptionEquals(cm.exception, NO_PROCESSUS_DETECTED)

        # Args
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave show a")
        self.assertExceptionEquals(cm.exception, NO_PROCESSUS_DETECTED)

        # Help
        self.assertStartsWith(
            self.debugger().execute("dave show -h"), "usage: dave show [-h]"
        )
        self.assertStartsWith(
            self.debugger().execute("dave show --help"), "usage: dave show [-h]"
        )
