from common import TestCaseBase, C_CPP_BUILD_DIR
from mocked import MockClient, patch_client_popen

from dave.common.raw_entity import RawEntityList


class TestCppStd(TestCaseBase.TYPE):
    BINARY = C_CPP_BUILD_DIR / "std"
    BINARY_HASH = "hihou"

    @patch_client_popen
    def test_minimal(self, _):
        # Set the breakpoints
        # self.debugger().set_breakpoint("main")
        self.debugger().set_breakpoint("std.cpp:57")
        self.debugger().set_breakpoint("std.cpp:81")
        self.debugger().set_breakpoint("std.cpp:91")
        self.debugger().set_breakpoint("std.cpp:98")

        # Start
        self.debugger().run()
        self.debugger().execute("dave show array")
        received = MockClient().receive_from_server()
        self.assertEqual(len(received), 1)
        self.assertIsInstance(received[0], RawEntityList)
        self.assertEqual(len(received[0].raw_updates), 1)
        # self.debugger().con()

        # TODO
        # self.assertEqual(1, 1)
