from common import TestCaseBase, C_CPP_BUILD_DIR, CommandError
from dave.common.raw_container import RawContainer
from dave.common.server_type import SERVER_TYPE, ServerType
from dave.server.process import DaveProcess
from mocked import MockClient, patch_client_popen

from dave.common.raw_entity import RawEntityList


class TestScope(TestCaseBase.TYPE):
    BINARY = C_CPP_BUILD_DIR / "custom_tests"

    @patch_client_popen
    def test_scope_up(self, _):
        # set the breakpoints
        self.debugger().set_breakpoints_at_tags("scope", [0, 2])

        SHOW_REGEX = r"Added (\w+) with ID ([0-9]+)"

        ################## scope::0 - Initial scope ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            matched = self.assertMatchsRegex(
                self.debugger().execute("dave show container_"),
                SHOW_REGEX,
            )
            container_id = int(matched.group(2))

            # Check we received 1 container
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 1, RawEntityList)
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)

        ################### scope::2 - upper scope ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            # Check we received one out-of-scope container
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 1, RawContainer.OutScopeUpdate)
            self.assertEqual(received[0].id, container_id)

    @patch_client_popen
    def test_scope_down(self, _):
        # set the breakpoints
        self.debugger().set_breakpoints_at_tags("scope", [1, 3, 4])

        SHOW_REGEX = r"Added (\w+) with ID ([0-9]+)"

        ################## scope::3 - Initial scope ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            matched = self.assertMatchsRegex(
                self.debugger().execute("dave show top_container"),
                SHOW_REGEX,
            )
            container_id = int(matched.group(2))

            # Check we received 1 container
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 1, RawEntityList)
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)

        ################### scope::1 - lower scope ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            # Check we received one out-of-scope container
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 1, RawContainer.OutScopeUpdate)
            self.assertEqual(received[0].id, container_id)

        ################### scope::4 - upper scope than initial ################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            # Check we received one out-of-scope container
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 1, RawContainer.OutScopeUpdate)
            self.assertEqual(received[0].id, container_id)
