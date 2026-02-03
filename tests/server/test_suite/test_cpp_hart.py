from common import TestCaseBase, CCppBinary
from mocked import MockClient, patch_client_popen

from dave.common.raw_entity import RawEntityList
from dave.common.raw_container import RawContainer
from dave.common.sample_type import SampleType

CONTAINER_2D_LAYOUTS = [
    RawContainer.Layout.CPX_2D,
    RawContainer.Layout.REAL_2D,
]


class TestCppHart(TestCaseBase.TYPE):
    BINARY = CCppBinary("hart_tests")

    def assertHartContainerInvariants(self, array: RawContainer):
        self.assertListEqual(array.possible_layout, CONTAINER_2D_LAYOUTS)
        self.assertEqual(array.dimensions_fixed, True)
        self.assertEqual(array.interleaved, False)

    @patch_client_popen
    def test_audio_buffer(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("audioBuffer", [1, 2])

        ################## audioBufferMultiChannel::1 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show buffer_f")
            self.debugger().execute("dave show buffer_d")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 2, RawEntityList)

            # buffer_f
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            raw_buffer_f: RawContainer = received[0].raw_entities[0]
            self.assertHartContainerInvariants(raw_buffer_f)
            self.assertTupleEqual(raw_buffer_f.original_shape, (2, 3))
            self.assertEqual(raw_buffer_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_buffer_f.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_buffer_f)
            self.assertPrettyPrinterEqual(
                "buffer_f",
                "2 channels 3 samples, min 0.0000E+00, max 0.0000E+00",
                [("dSparkline[0]", '"[0(3)]"'), ("dSparkline[1]", '"[0(3)]"')],
            )

            # buffer_d
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_buffer_d: RawContainer = received[1].raw_entities[0]
            self.assertHartContainerInvariants(raw_buffer_d)
            self.assertTupleEqual(raw_buffer_d.original_shape, (2, 3))
            self.assertEqual(raw_buffer_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(raw_buffer_d.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_buffer_d)
            self.assertPrettyPrinterEqual(
                "buffer_d",
                "2 channels 3 samples, min 0.0000E+00, max 0.0000E+00",
                [("dSparkline[0]", '"[0(3)]"'), ("dSparkline[1]", '"[0(3)]"')],
            )

        ############ audioBufferMultiChannel::2 - (0,0,0),(1.0,-1.0,0.0) ############
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 2, RawContainer.InScopeUpdate)

            # buffer_f
            self.assertEqual(received[0].id, raw_buffer_f.id)
            self.assertTupleEqual(received[0].shape, raw_buffer_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0), raw_buffer_f, received[0]
            )
            self.assertPrettyPrinterEqual(
                "buffer_f",
                "2 channels 3 samples, min -1.0000E+00, max 1.0000E+00",
                [("dSparkline[0]", '"[0(3)]"'), ("dSparkline[1]", '"[‾x0]"')],
            )

            # buffer_d
            self.assertEqual(received[1].id, raw_buffer_d.id)
            self.assertTupleEqual(received[1].shape, raw_buffer_d.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0), raw_buffer_d, received[1]
            )
            self.assertPrettyPrinterEqual(
                "buffer_d",
                "2 channels 3 samples, min -1.0000E+00, max 1.0000E+00",
                [("dSparkline[0]", '"[0(3)]"'), ("dSparkline[1]", '"[‾x0]"')],
            )
