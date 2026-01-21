from typing import List, Tuple
import struct

from common import TestCaseBase, C_CPP_BUILD_DIR
from mocked import MockClient, patch_client_popen

from dave.common.raw_entity import RawEntity, RawEntityList, RawEntityUpdates
from dave.common.raw_container import RawContainer
from dave.common.sample_type import SampleType

CONTAINER_2D_LAYOUTS = [
    RawContainer.Layout.CPX_2D,
    RawContainer.Layout.REAL_2D,
]


class TestCppJuce(TestCaseBase.TYPE):
    BINARY = C_CPP_BUILD_DIR / "juce_tests"
    BINARY_HASH = "hihou"

    def assertJuceContainerInvariants(self, array: RawContainer):
        self.assertListEqual(array.possible_layout, CONTAINER_2D_LAYOUTS)
        self.assertEqual(array.dimensions_fixed, True)
        self.assertEqual(array.interleaved, False)

    @patch_client_popen
    def test_buffer_mono(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("audioBufferMono", [1, 2])

        ################## audioBufferMono::1 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show buffer_f")
            self.debugger().execute("dave show buffer_d")
            self.debugger().execute("dave show buffer_f_p")
            self.debugger().execute("dave show buffer_d_p")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawEntityList)

            # buffer_f
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            raw_buffer_f: RawContainer = received[0].raw_entities[0]
            self.assertJuceContainerInvariants(raw_buffer_f)
            self.assertTupleEqual(raw_buffer_f.original_shape, (1, 3))
            self.assertEqual(raw_buffer_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_buffer_f.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_buffer_f)

        ################## audioBufferMono::2 - (1, -1, 0) ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # buffer_f
            self.assertEqual(received[0].id, raw_buffer_f.id)
            self.assertTupleEqual(received[0].shape, raw_buffer_f.original_shape)
            self.assertContainerContent((1.0, -1.0, 0.0), raw_buffer_f, received[0])
            self.assertPrettyPrinterEqual(
                "buffer_f",
                "1 channels 3 samples, min -1.0000E+00, max 1.0000E+00",
                [("dSparkline[0]", '"[‾x0]"')],
            )
