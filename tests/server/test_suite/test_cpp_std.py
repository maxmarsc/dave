from common import TestCaseBase, C_CPP_BUILD_DIR


class TestCppStd(TestCaseBase.TYPE):
    BINARY = C_CPP_BUILD_DIR / "std"
    BINARY_HASH = "hihou"

    def test_minimal(self):
        # Set the breakpoints
        self.debugger().set_breakpoint("main")
        self.debugger().set_breakpoint("std.cpp:57")
        self.debugger().set_breakpoint("std.cpp:81")
        self.debugger().set_breakpoint("std.cpp:91")
        self.debugger().set_breakpoint("std.cpp:98")

        # Start
        self.debugger().run()
        self.debugger().con()

        # TODO
        self.assertEqual(1, 2)
