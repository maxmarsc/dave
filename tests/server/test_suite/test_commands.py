from typing import List, Tuple
import struct

from common import TestCaseBase, C_CPP_BUILD_DIR, CommandError
from dave.common.raw_container import RawContainer
from dave.common.server_type import SERVER_TYPE, ServerType
from dave.server.process import DaveProcess
from mocked import MockClient, patch_client_popen

from dave.common.raw_entity import RawEntityList

NO_PROCESSUS_DETECTED = CommandError("No processus detected")


class TestCommands(TestCaseBase.TYPE):
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
    def test_show_not_parsable(self, _):
        # Set the breakpoint
        self.debugger().set_breakpoints_at_tags("daveCommands", [1])

        self.debugger().run()
        with self.failFastSubTestAtLocation():
            # too many args
            with self.assertRaises(CommandError) as cm:
                self.debugger().execute("dave show container container_ref")
            self.assertIsCommandErrorWith(cm.exception, "usage: dave show [-h]")

            # invalid long flag
            with self.assertRaises(CommandError) as cm:
                self.debugger().execute("dave show --leroy-jenkins container")
            self.assertIsCommandErrorWith(cm.exception, "usage: dave show [-h]")

            # invalid long flag
            with self.assertRaises(CommandError) as cm:
                self.debugger().execute("dave show -z container")
            self.assertIsCommandErrorWith(cm.exception, "usage: dave show [-h]")

    @patch_client_popen
    def test_show_initialized(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("daveCommands", [1, 2])

        SHOW_REGEX = r"Added (\w+) with ID ([0-9]+)"

        ################## daveCommands::1 - Show ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            matched = self.assertMatchsRegex(
                self.debugger().execute("dave show container"),
                SHOW_REGEX,
            )
            self.assertIsIn("container", matched.group(1))
            matched = self.assertMatchsRegex(
                self.debugger().execute("dave show container_ref"),
                SHOW_REGEX,
            )
            self.assertIsIn("container_ref", matched.group(1))

            # Check we receive the right amount of containers
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 2, RawEntityList)
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)

            raw_container: RawContainer = received[0].raw_entities[0]
            raw_container_ref: RawContainer = received[1].raw_entities[0]

            # check the order of reception
            self.assertEqual(raw_container.name, "container")
            self.assertEqual(raw_container_ref.name, "container_ref")

            # check the scope
            self.assertTrue(raw_container.in_scope)
            self.assertTrue(raw_container_ref.in_scope)

        ################## daveCommands::2 - Update ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 2, RawContainer.InScopeUpdate)

            # Check the ids
            self.assertEqual(raw_container.id, received[0].id)
            self.assertEqual(raw_container_ref.id, received[1].id)

    @patch_client_popen
    def test_show_not_itialized(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("daveCommands", [0, 1])

        ################## daveCommands::0 - Show ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show container")
            self.debugger().execute("dave show container_ref")

            # Check we receive the right amount of containers
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 2, RawEntityList)
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)

            raw_container: RawContainer = received[0].raw_entities[0]
            raw_container_ref: RawContainer = received[1].raw_entities[0]

            # check the order of reception
            self.assertEqual(raw_container.name, "container")
            self.assertEqual(raw_container_ref.name, "container_ref")

            # check the scope
            self.assertFalse(raw_container.in_scope)
            self.assertFalse(raw_container_ref.in_scope)

        ################## daveCommands::1 - Update ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()

            self.assertIsNotNone(SERVER_TYPE)
            # lldbSBValue are dynamic views of variables, this means it will update
            # the reference's address once initialized
            if SERVER_TYPE == ServerType.LLDB:
                self.assertIsListOf(received, 2, RawContainer.InScopeUpdate)
            # gd.Value are snapshots of variables, this means it will NOT update
            # the reference's address once initialized => It will always be out-of-scope
            elif SERVER_TYPE == ServerType.GDB:
                self.assertIsInstance(received[0], RawContainer.InScopeUpdate)
                self.assertIsInstance(received[1], RawContainer.OutScopeUpdate)

            # Check the ids
            self.assertEqual(raw_container.id, received[0].id)
            self.assertEqual(raw_container_ref.id, received[1].id)

    @patch_client_popen
    def test_show_all_initialized(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("daveCommands", [1, 2])

        ################## daveCommands::1 - Show ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show")

            # Check we receive the right amount of containers
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 1, RawEntityList)
            self.assertEqual(len(received[0].raw_entities), 2)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            self.assertIsInstance(received[0].raw_entities[1], RawContainer)

            NAMES = ("container", "container_ref")
            raw_first: RawContainer = received[0].raw_entities[0]
            raw_second: RawContainer = received[0].raw_entities[1]

            # check the names
            self.assertIsIn(raw_first.name, NAMES)
            self.assertIsIn(raw_second.name, NAMES)
            self.assertNotEqual(raw_first.name, raw_second.name)

            # check the IDs
            self.assertNotEqual(raw_first.id, raw_second.id)

            # check the scope
            self.assertTrue(raw_first.in_scope)
            self.assertTrue(raw_second.in_scope)

        ################## daveCommands::2 - Update ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 2, RawContainer.InScopeUpdate)

            # Check the ids
            self.assertEqual(raw_first.id, received[0].id)
            self.assertEqual(raw_second.id, received[1].id)

    @patch_client_popen
    def test_show_all_not_itialized(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("daveCommands", [0, 1])

        ################## daveCommands::0 - Show ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show")

            # Check we receive the right amount of containers
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 1, RawEntityList)
            self.assertEqual(len(received[0].raw_entities), 2)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            self.assertIsInstance(received[0].raw_entities[1], RawContainer)

            NAMES = ("container", "container_ref")
            raw_first: RawContainer = received[0].raw_entities[0]
            raw_second: RawContainer = received[0].raw_entities[1]

            # check the names
            self.assertIsIn(raw_first.name, NAMES)
            self.assertIsIn(raw_second.name, NAMES)
            self.assertNotEqual(raw_first.name, raw_second.name)

            # check the IDs
            self.assertNotEqual(raw_first.id, raw_second.id)

            # check the scope
            self.assertFalse(raw_first.in_scope)
            self.assertFalse(raw_second.in_scope)

        # ################## daveCommands::1 - Update ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()

            self.assertIsNotNone(SERVER_TYPE)
            # lldbSBValue are dynamic views of variables, this means it will update
            # the reference's address once initialized
            if SERVER_TYPE == ServerType.LLDB:
                self.assertIsListOf(received, 2, RawContainer.InScopeUpdate)
            # gd.Value are snapshots of variables, this means it will NOT update
            # the reference's address once initialized => It will always be out-of-scope
            elif SERVER_TYPE == ServerType.GDB:
                if raw_second.name == "container_ref":
                    self.assertIsInstance(received[0], RawContainer.InScopeUpdate)
                    self.assertIsInstance(received[1], RawContainer.OutScopeUpdate)
                else:
                    self.assertIsInstance(received[0], RawContainer.OutScopeUpdate)
                    self.assertIsInstance(received[1], RawContainer.InScopeUpdate)

            # Check the ids - the order should match
            self.assertEqual(raw_first.id, received[0].id)
            self.assertEqual(raw_second.id, received[1].id)

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
    def test_inspect_not_parsable(self, _):
        # Set the breakpoint
        self.debugger().set_breakpoints_at_tags("daveCommands", [1])

        self.debugger().run()
        with self.failFastSubTestAtLocation():
            # too many args
            with self.assertRaises(CommandError) as cm:
                self.debugger().execute("dave inspect container container_ref")
            self.assertIsCommandErrorWith(cm.exception, "usage: dave inspect [-h]")

            # not enough args
            with self.assertRaises(CommandError) as cm:
                self.debugger().execute("dave inspect")
            self.assertIsCommandErrorWith(cm.exception, "usage: dave inspect [-h]")

            # invalid long flag
            with self.assertRaises(CommandError) as cm:
                self.debugger().execute("dave inspect --leroy-jenkins container")
            self.assertIsCommandErrorWith(cm.exception, "usage: dave inspect [-h]")

            # invalid long flag
            with self.assertRaises(CommandError) as cm:
                self.debugger().execute("dave inspect -z container")
            self.assertIsCommandErrorWith(cm.exception, "usage: dave inspect [-h]")

    @patch_client_popen
    def test_inspect(self, _):
        # Set the breakpoint
        self.debugger().set_breakpoints_at_tags("daveCommands", [1])

        INSPECT_REGEX = r"Type:\s(.*)\nLang:\sCPP"

        self.debugger().run()
        with self.failFastSubTestAtLocation():
            # vanilla type
            self.assertMatchsRegex(
                self.debugger().execute("dave inspect kBlockSize"),
                INSPECT_REGEX,
            )

            # Custom type
            matched = self.assertMatchsRegex(
                self.debugger().execute("dave inspect container"),
                INSPECT_REGEX,
            )
            self.assertIsIn("DaveCustomInterleavedContainerVec", matched.group(1))

            # Reference to custom type
            matched = self.assertMatchsRegex(
                self.debugger().execute("dave inspect container_ref"),
                INSPECT_REGEX,
            )
            self.assertIsIn("DaveCustomInterleavedContainerVec", matched.group(1))

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
    def test_delete_not_parsable(self, _):
        # Set the breakpoint
        self.debugger().set_breakpoints_at_tags("daveCommands", [1])

        self.debugger().run()
        with self.failFastSubTestAtLocation():
            # too many args
            with self.assertRaises(CommandError) as cm:
                self.debugger().execute("dave delete ID_1 ID_2")
            self.assertIsCommandErrorWith(cm.exception, "usage: dave delete [-h]")

            # not enough args
            with self.assertRaises(CommandError) as cm:
                self.debugger().execute("dave delete ID_1 ID_2")
            self.assertIsCommandErrorWith(cm.exception, "usage: dave delete [-h]")

            # invalid long flag
            with self.assertRaises(CommandError) as cm:
                self.debugger().execute("dave delete --leroy-jenkins ID_1")
            self.assertIsCommandErrorWith(cm.exception, "usage: dave delete [-h]")

            # invalid short flag
            with self.assertRaises(CommandError) as cm:
                self.debugger().execute("dave delete -z ID_1")
            self.assertIsCommandErrorWith(cm.exception, "usage: dave delete [-h]")

    @patch_client_popen
    def test_delete_with_id(self, _):
        # Set the breakpoint
        self.debugger().set_breakpoints_at_tags("daveCommands", [1, 2, 3])

        SHOW_REGEX = r"Added (\w+) with ID ([0-9]+)"

        ################## daveCommands::1 - Show ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            # First, show to get the IDs
            matched = self.assertMatchsRegex(
                self.debugger().execute("dave show container"),
                SHOW_REGEX,
            )
            container_id = matched.group(2)
            matched = self.assertMatchsRegex(
                self.debugger().execute("dave show container_ref"),
                SHOW_REGEX,
            )
            container_ref_id = matched.group(2)

            # Clean the received data
            MockClient().receive_from_server()

            # Now, delete using the IDs
            self.debugger().execute(f"dave delete {container_id}")
            self.debugger().execute(f"dave delete {container_ref_id}")

            # Re-add the containers for long time check
            matched = self.assertMatchsRegex(
                self.debugger().execute("dave show container"),
                SHOW_REGEX,
            )
            container_id = matched.group(2)
            matched = self.assertMatchsRegex(
                self.debugger().execute("dave show container_ref"),
                SHOW_REGEX,
            )
            container_ref_id = matched.group(2)

        # consume the delete messages client-side
        delete_msg = MockClient().receive_from_server()[:2]
        self.assertIsListOf(delete_msg, 2, DaveProcess.DeleteMessage)

        ################## daveCommands::2 - Update ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            # Check we receive the right amount of containers
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 2, RawContainer.InScopeUpdate)

            # Now, delete again using the IDs
            self.debugger().execute(f"dave delete {container_id}")
            self.debugger().execute(f"dave delete {container_ref_id}")

        # consume the delete messages client-side
        delete_msg = MockClient().receive_from_server()[:2]
        self.assertIsListOf(delete_msg, 2, DaveProcess.DeleteMessage)

        ################## daveCommands::3 - Update ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            # At this point we shoudln't receive anything
            received = MockClient().receive_from_server()
            self.assertEqual(len(received), 0)

    @patch_client_popen
    def test_delete_with_name(self, _):
        # Set the breakpoint
        self.debugger().set_breakpoints_at_tags("daveCommands", [1, 2, 3])

        SHOW_REGEX = r"Added (\w+) with ID ([0-9]+)"

        ################## daveCommands::1 - Show ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            # First, show
            self.assertMatchsRegex(
                self.debugger().execute("dave show container"),
                SHOW_REGEX,
            )
            self.assertMatchsRegex(
                self.debugger().execute("dave show container_ref"),
                SHOW_REGEX,
            )

            # Clean the received data
            MockClient().receive_from_server()

            # Now, delete using the IDs
            self.debugger().execute(f"dave delete container")
            self.debugger().execute(f"dave delete container_ref")

            # Re-add the containers for long time check
            self.assertMatchsRegex(
                self.debugger().execute("dave show container"),
                SHOW_REGEX,
            )
            self.assertMatchsRegex(
                self.debugger().execute("dave show container_ref"),
                SHOW_REGEX,
            )

        # consume the delete messages client-side
        delete_msg = MockClient().receive_from_server()[:2]
        self.assertIsListOf(delete_msg, 2, DaveProcess.DeleteMessage)

        ################## daveCommands::2 - Update ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            # Check we receive the right amount of containers
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 2, RawContainer.InScopeUpdate)

            # Now, delete again using the IDs
            self.debugger().execute(f"dave delete container")
            self.debugger().execute(f"dave delete container_ref")

        # consume the delete messages client-side
        delete_msg = MockClient().receive_from_server()[:2]
        self.assertIsListOf(delete_msg, 2, DaveProcess.DeleteMessage)

        ################## daveCommands::3 - Update ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            # At this point we shoudln't receive anything
            received = MockClient().receive_from_server()
            self.assertEqual(len(received), 0)

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
