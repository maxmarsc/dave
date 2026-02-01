from common import TestCaseBase, C_CPP_BUILD_DIR
from mocked import patch_client_popen


class TestContainerPrettyPrinters(TestCaseBase.TYPE):
    BINARY = C_CPP_BUILD_DIR / "custom_tests"

    @patch_client_popen
    def test_pretty_container_planar(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("containerPrettyPrinters", [1, 2, 3])

        ################## containerPrettyPrinters::1 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.assertPrettyPrinterEqual(
                "container",
                "2 channels 11 samples, min 0.0000E+00, max 0.0000E+00",
                [("dSparkline[0]", '"[0(11)]"'), ("dSparkline[1]", '"[0(11)]"')],
            )

        ################## containerPrettyPrinters::2 - Ramps ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            self.assertPrettyPrinterEqual(
                "container",
                "2 channels 11 samples, min -1.0000E+00, max 1.0000E+00",
                [("dSparkline[0]", '"[‾⎺⎻—x⎼⎽_]"'), ("dSparkline[1]", '"[_⎽⎼—x⎻⎺‾]"')],
            )

        ######### containerPrettyPrinters::3 - Numeric special values ###########
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            self.assertPrettyPrinterEqual(
                "container",
                "2 channels 11 samples, min -INF, max INF",
                [("dSparkline[0]", '"[IE⎻—N—⎼EI]"'), ("dSparkline[1]", '"[_⎽⎼—x⎻⎺‾]"')],
            )
