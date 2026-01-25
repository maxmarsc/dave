from typing import List, Tuple
import struct

from common import TestCaseBase, C_CPP_BUILD_DIR, CommandError
from mocked import MockClient, patch_client_popen

NO_PROCESSUS_DETECTED = CommandError("No processus detected")


class TestContainerPrettyPrinters(TestCaseBase.TYPE):
    BINARY = C_CPP_BUILD_DIR / "custom_tests"
    BINARY_HASH = "hihou"

    @patch_client_popen
    def test_show_parsable_no_processus(self, _):
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

    @patch_client_popen
    def test_show_not_parsable_no_processus(self, _):
        # too many args
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave show a b ")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave show [-h]")

        # invalid long flag
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave show --leroy-jenkins a")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave show [-h]")

        # invalid long flag
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave show -z a")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave show [-h]")

    @patch_client_popen
    def test_inspect_parsable_no_processus(self, _):
        # Args
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave inspect a")
        self.assertExceptionEquals(cm.exception, NO_PROCESSUS_DETECTED)

        # Help
        self.assertStartsWith(
            self.debugger().execute("dave inspect -h"), "usage: dave inspect [-h]"
        )
        self.assertStartsWith(
            self.debugger().execute("dave inspect --help"), "usage: dave inspect [-h]"
        )

    @patch_client_popen
    def test_inspect_not_parsable_no_processus(self, _):
        # too many args
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave inspect a b")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave inspect [-h]")

        # not enough args
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave inspect")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave inspect [-h]")

        # invalid long flag
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave inspect --leroy-jenkins a")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave inspect [-h]")

        # invalid long flag
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave inspect -z a")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave inspect [-h]")

    @patch_client_popen
    def test_delete_parsable_no_processus(self, _):
        # Args
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave delete ID")
        self.assertExceptionEquals(cm.exception, NO_PROCESSUS_DETECTED)

        # Help
        self.assertStartsWith(
            self.debugger().execute("dave delete -h"), "usage: dave delete [-h]"
        )
        self.assertStartsWith(
            self.debugger().execute("dave delete --help"), "usage: dave delete [-h]"
        )

    @patch_client_popen
    def test_delete_not_parsable_no_processus(self, _):
        # too many args
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave delete a b")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave delete [-h]")

        # not enough args
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave delete")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave delete [-h]")

        # invalid long flag
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave delete --leroy-jenkins a")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave delete [-h]")

        # invalid long flag
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave delete -z a")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave delete [-h]")

    @patch_client_popen
    def test_freeze_parsable_no_processus(self, _):
        # Args
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave freeze ID")
        self.assertExceptionEquals(cm.exception, NO_PROCESSUS_DETECTED)

        # Help
        self.assertStartsWith(
            self.debugger().execute("dave freeze -h"), "usage: dave freeze [-h]"
        )
        self.assertStartsWith(
            self.debugger().execute("dave freeze --help"), "usage: dave freeze [-h]"
        )

    @patch_client_popen
    def test_freeze_not_parsable_no_processus(self, _):
        # too many args
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave freeze a b")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave freeze [-h]")

        # not enough args
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave freeze")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave freeze [-h]")

        # invalid long flag
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave freeze --leroy-jenkins a")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave freeze [-h]")

        # invalid long flag
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave freeze -z a")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave freeze [-h]")

    @patch_client_popen
    def test_concat_parsable_no_processus(self, _):
        # Args
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave concat ID")
        self.assertExceptionEquals(cm.exception, NO_PROCESSUS_DETECTED)

        # Help
        self.assertStartsWith(
            self.debugger().execute("dave concat -h"), "usage: dave concat [-h]"
        )
        self.assertStartsWith(
            self.debugger().execute("dave concat --help"), "usage: dave concat [-h]"
        )

    @patch_client_popen
    def test_concat_not_parsable_no_processus(self, _):
        # too many args
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave concat a b")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave concat [-h]")

        # not enough args
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave concat")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave concat [-h]")

        # invalid long flag
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave concat --leroy-jenkins a")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave concat [-h]")

        # invalid long flag
        with self.assertRaises(CommandError) as cm:
            self.debugger().execute("dave concat -z a")
        self.assertIsCommandErrorWith(cm.exception, "usage: dave concat [-h]")
