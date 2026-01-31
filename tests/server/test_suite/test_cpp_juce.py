from typing import List, Tuple
import struct

from common import TestCaseBase, C_CPP_BUILD_DIR
from dave.common.raw_iir import RawIir
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
            self.debugger().execute("dave show buffer_f_p")
            self.debugger().execute("dave show buffer_d")
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
            self.assertPrettyPrinterEqual(
                "buffer_f",
                "1 channels 3 samples, min 0.0000E+00, max 0.0000E+00",
                [("dSparkline[0]", '"[0(3)]"')],
            )

            # buffer_f_p
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_buffer_f_p: RawContainer = received[1].raw_entities[0]
            self.assertJuceContainerInvariants(raw_buffer_f_p)
            self.assertTupleEqual(raw_buffer_f_p.original_shape, (1, 3))
            self.assertEqual(raw_buffer_f_p.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_buffer_f_p.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_buffer_f_p)
            self.assertPrettyPrinterEqual(
                "buffer_f_p",
                "1 channels 3 samples, min 0.0000E+00, max 0.0000E+00",
                [("dSparkline[0]", '"[0(3)]"')],
            )

            # buffer_d
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawContainer)
            raw_buffer_d: RawContainer = received[2].raw_entities[0]
            self.assertJuceContainerInvariants(raw_buffer_d)
            self.assertTupleEqual(raw_buffer_d.original_shape, (1, 3))
            self.assertEqual(raw_buffer_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(raw_buffer_d.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_buffer_d)
            self.assertPrettyPrinterEqual(
                "buffer_d",
                "1 channels 3 samples, min 0.0000E+00, max 0.0000E+00",
                [("dSparkline[0]", '"[0(3)]"')],
            )

            # buffer_d_p
            self.assertEqual(len(received[3].raw_entities), 1)
            self.assertIsInstance(received[3].raw_entities[0], RawContainer)
            raw_buffer_d_p: RawContainer = received[3].raw_entities[0]
            self.assertJuceContainerInvariants(raw_buffer_f)
            self.assertTupleEqual(raw_buffer_d_p.original_shape, (1, 3))
            self.assertEqual(raw_buffer_d_p.sample_type, SampleType.DOUBLE)
            self.assertEqual(raw_buffer_d_p.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_buffer_d_p)
            self.assertPrettyPrinterEqual(
                "buffer_d_p",
                "1 channels 3 samples, min 0.0000E+00, max 0.0000E+00",
                [("dSparkline[0]", '"[0(3)]"')],
            )

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

            # buffer_f_p
            self.assertEqual(received[1].id, raw_buffer_f_p.id)
            self.assertTupleEqual(received[1].shape, raw_buffer_f_p.original_shape)
            self.assertContainerContent((1.0, -1.0, 0.0), raw_buffer_f_p, received[1])
            self.assertPrettyPrinterEqual(
                "buffer_f_p",
                "1 channels 3 samples, min -1.0000E+00, max 1.0000E+00",
                [("dSparkline[0]", '"[‾x0]"')],
            )

            # buffer_d
            self.assertEqual(received[2].id, raw_buffer_d.id)
            self.assertTupleEqual(received[2].shape, raw_buffer_d.original_shape)
            self.assertContainerContent((1.0, -1.0, 0.0), raw_buffer_d, received[2])
            self.assertPrettyPrinterEqual(
                "buffer_d",
                "1 channels 3 samples, min -1.0000E+00, max 1.0000E+00",
                [("dSparkline[0]", '"[‾x0]"')],
            )

            # buffer_d_p
            self.assertEqual(received[3].id, raw_buffer_d_p.id)
            self.assertTupleEqual(received[3].shape, raw_buffer_d_p.original_shape)
            self.assertContainerContent((1.0, -1.0, 0.0), raw_buffer_d_p, received[3])
            self.assertPrettyPrinterEqual(
                "buffer_d_p",
                "1 channels 3 samples, min -1.0000E+00, max 1.0000E+00",
                [("dSparkline[0]", '"[‾x0]"')],
            )

    @patch_client_popen
    def test_buffer_multi_channel(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("audioBufferMultiChannel", [1, 2])

        ################## audioBufferMultiChannel::1 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show buffer_f")
            self.debugger().execute("dave show buffer_f_p")
            self.debugger().execute("dave show buffer_d")
            self.debugger().execute("dave show buffer_d_p")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawEntityList)

            # buffer_f
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            raw_buffer_f: RawContainer = received[0].raw_entities[0]
            self.assertJuceContainerInvariants(raw_buffer_f)
            self.assertTupleEqual(raw_buffer_f.original_shape, (2, 3))
            self.assertEqual(raw_buffer_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_buffer_f.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_buffer_f)
            self.assertPrettyPrinterEqual(
                "buffer_f",
                "2 channels 3 samples, min 0.0000E+00, max 0.0000E+00",
                [("dSparkline[0]", '"[0(3)]"'), ("dSparkline[1]", '"[0(3)]"')],
            )

            # buffer_f_p
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_buffer_f_p: RawContainer = received[1].raw_entities[0]
            self.assertJuceContainerInvariants(raw_buffer_f_p)
            self.assertTupleEqual(raw_buffer_f_p.original_shape, (2, 3))
            self.assertEqual(raw_buffer_f_p.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_buffer_f_p.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_buffer_f_p)
            self.assertPrettyPrinterEqual(
                "buffer_f_p",
                "2 channels 3 samples, min 0.0000E+00, max 0.0000E+00",
                [("dSparkline[0]", '"[0(3)]"'), ("dSparkline[1]", '"[0(3)]"')],
            )

            # buffer_d
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawContainer)
            raw_buffer_d: RawContainer = received[2].raw_entities[0]
            self.assertJuceContainerInvariants(raw_buffer_d)
            self.assertTupleEqual(raw_buffer_d.original_shape, (2, 3))
            self.assertEqual(raw_buffer_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(raw_buffer_d.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_buffer_d)
            self.assertPrettyPrinterEqual(
                "buffer_d",
                "2 channels 3 samples, min 0.0000E+00, max 0.0000E+00",
                [("dSparkline[0]", '"[0(3)]"'), ("dSparkline[1]", '"[0(3)]"')],
            )

            # buffer_d_p
            self.assertEqual(len(received[3].raw_entities), 1)
            self.assertIsInstance(received[3].raw_entities[0], RawContainer)
            raw_buffer_d_p: RawContainer = received[3].raw_entities[0]
            self.assertJuceContainerInvariants(raw_buffer_d_p)
            self.assertTupleEqual(raw_buffer_d_p.original_shape, (2, 3))
            self.assertEqual(raw_buffer_d_p.sample_type, SampleType.DOUBLE)
            self.assertEqual(raw_buffer_d_p.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_buffer_d_p)
            self.assertPrettyPrinterEqual(
                "buffer_d_p",
                "2 channels 3 samples, min 0.0000E+00, max 0.0000E+00",
                [("dSparkline[0]", '"[0(3)]"'), ("dSparkline[1]", '"[0(3)]"')],
            )

        ############ audioBufferMultiChannel::2 - (0,0,0),(1.0,-1.0,0.0) ############
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

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

            # buffer_f_p
            self.assertEqual(received[1].id, raw_buffer_f_p.id)
            self.assertTupleEqual(received[1].shape, raw_buffer_f_p.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0), raw_buffer_f_p, received[1]
            )
            self.assertPrettyPrinterEqual(
                "buffer_f_p",
                "2 channels 3 samples, min -1.0000E+00, max 1.0000E+00",
                [("dSparkline[0]", '"[0(3)]"'), ("dSparkline[1]", '"[‾x0]"')],
            )

            # buffer_d
            self.assertEqual(received[2].id, raw_buffer_d.id)
            self.assertTupleEqual(received[2].shape, raw_buffer_d.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0), raw_buffer_d, received[2]
            )
            self.assertPrettyPrinterEqual(
                "buffer_d",
                "2 channels 3 samples, min -1.0000E+00, max 1.0000E+00",
                [("dSparkline[0]", '"[0(3)]"'), ("dSparkline[1]", '"[‾x0]"')],
            )

            # buffer_d_p
            self.assertEqual(received[3].id, raw_buffer_d_p.id)
            self.assertTupleEqual(received[3].shape, raw_buffer_d_p.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0), raw_buffer_d_p, received[3]
            )
            self.assertPrettyPrinterEqual(
                "buffer_d_p",
                "2 channels 3 samples, min -1.0000E+00, max 1.0000E+00",
                [("dSparkline[0]", '"[0(3)]"'), ("dSparkline[1]", '"[‾x0]"')],
            )

    @patch_client_popen
    def test_audio_block(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("audioBlock", [1, 2])

        ################## audioBlock::0 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show block_f")
            self.debugger().execute("dave show block_d")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 2, RawEntityList)

            # block_f
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            raw_block_f: RawContainer = received[0].raw_entities[0]
            self.assertJuceContainerInvariants(raw_block_f)
            self.assertTupleEqual(raw_block_f.original_shape, (2, 3))
            self.assertEqual(raw_block_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_block_f.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_block_f)
            self.assertPrettyPrinterEqual(
                "block_f",
                "2 channels 3 samples, min 0.0000E+00, max 0.0000E+00",
                [("dSparkline[0]", '"[0(3)]"'), ("dSparkline[1]", '"[0(3)]"')],
            )

            # block_d
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_block_d: RawContainer = received[1].raw_entities[0]
            self.assertJuceContainerInvariants(raw_block_d)
            self.assertTupleEqual(raw_block_d.original_shape, (2, 3))
            self.assertEqual(raw_block_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(raw_block_d.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_block_d)
            self.assertPrettyPrinterEqual(
                "block_d",
                "2 channels 3 samples, min 0.0000E+00, max 0.0000E+00",
                [("dSparkline[0]", '"[0(3)]"'), ("dSparkline[1]", '"[0(3)]"')],
            )

        ############ audioBlock::2 - (0,0,0),(1.0,-1.0,0.0) ############
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 2, RawContainer.InScopeUpdate)

            # block_f
            self.assertEqual(received[0].id, raw_block_f.id)
            self.assertTupleEqual(received[0].shape, raw_block_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0), raw_block_f, received[0]
            )
            self.assertPrettyPrinterEqual(
                "block_f",
                "2 channels 3 samples, min -1.0000E+00, max 1.0000E+00",
                [("dSparkline[0]", '"[0(3)]"'), ("dSparkline[1]", '"[‾x0]"')],
            )

            # block_d
            self.assertEqual(received[1].id, raw_block_d.id)
            self.assertTupleEqual(received[1].shape, raw_block_d.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0), raw_block_d, received[1]
            )
            self.assertPrettyPrinterEqual(
                "block_d",
                "2 channels 3 samples, min -1.0000E+00, max 1.0000E+00",
                [("dSparkline[0]", '"[0(3)]"'), ("dSparkline[1]", '"[‾x0]"')],
            )

    @patch_client_popen
    def test_iir_coeffs(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("iirSOS", [1])

        ################## iirSOS::1 - Initial state ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show coeffs_f_fo")
            self.debugger().execute("dave show coeffs_d_fo")
            self.debugger().execute("dave show coeffs_f_so")
            self.debugger().execute("dave show coeffs_d_so")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawEntityList)

            # coeffs_f_fo
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawIir)
            raw_coeffs_f_fo: RawIir = received[0].raw_entities[0]
            self.assertIsInstance(raw_coeffs_f_fo.coeffs, RawIir.SOSCoeffs)
            # Make sure we have the right number of sections
            self.assertEqual(len(raw_coeffs_f_fo.coeffs.values), 1)
            self.assertEqual(len(raw_coeffs_f_fo.coeffs.values[0]), 6)
            # First order filter => b2 == 0 & a2 == 0
            self.assertLess(abs(raw_coeffs_f_fo.coeffs.values[0][2]), 1e-12)
            self.assertLess(abs(raw_coeffs_f_fo.coeffs.values[0][5]), 1e-12)

            # coeffs_d_fo
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawIir)
            raw_coeffs_d_fo: RawIir = received[1].raw_entities[0]
            self.assertIsInstance(raw_coeffs_d_fo.coeffs, RawIir.SOSCoeffs)
            # Make sure we have the right number of sections
            self.assertEqual(len(raw_coeffs_d_fo.coeffs.values), 1)
            self.assertEqual(len(raw_coeffs_d_fo.coeffs.values[0]), 6)
            # First order filter => b2 == 0 & a2 == 0
            self.assertLess(abs(raw_coeffs_d_fo.coeffs.values[0][2]), 1e-12)
            self.assertLess(abs(raw_coeffs_d_fo.coeffs.values[0][5]), 1e-12)

            # coeffs_f_so
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawIir)
            raw_coeffs_f_so: RawIir = received[2].raw_entities[0]
            self.assertIsInstance(raw_coeffs_f_so.coeffs, RawIir.SOSCoeffs)
            # Make sure we have the right number of sections
            self.assertEqual(len(raw_coeffs_f_so.coeffs.values), 1)
            self.assertEqual(len(raw_coeffs_f_so.coeffs.values[0]), 6)
            # Second order filter => b2 != 0 || a2 != 0
            try:
                self.assertGreater(abs(raw_coeffs_f_so.coeffs.values[0][2]), 1e-12)
            except AssertionError:
                self.assertGreater(abs(raw_coeffs_f_so.coeffs.values[0][5]), 1e-12)

            # coeffs_d_so
            self.assertEqual(len(received[3].raw_entities), 1)
            self.assertIsInstance(received[3].raw_entities[0], RawIir)
            raw_coeffs_d_so: RawIir = received[3].raw_entities[0]
            self.assertIsInstance(raw_coeffs_d_so.coeffs, RawIir.SOSCoeffs)
            # Make sure we have the right number of sections
            self.assertEqual(len(raw_coeffs_d_so.coeffs.values), 1)
            self.assertEqual(len(raw_coeffs_d_so.coeffs.values[0]), 6)
            # Second order filter => b2 != 0 || a2 != 0
            try:
                self.assertGreater(abs(raw_coeffs_d_so.coeffs.values[0][2]), 1e-12)
            except AssertionError:
                self.assertGreater(abs(raw_coeffs_d_so.coeffs.values[0][5]), 1e-12)

    @patch_client_popen
    def test_iir_filter(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("iirSOS", [1])

        ################## iirSOS::1 - Initial state ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show filter_f_fo")
            self.debugger().execute("dave show filter_d_fo")
            self.debugger().execute("dave show filter_f_so")
            self.debugger().execute("dave show filter_d_so")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawEntityList)

            # filter_f_fo
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawIir)
            raw_filter_f_fo: RawIir = received[0].raw_entities[0]
            self.assertIsInstance(raw_filter_f_fo.coeffs, RawIir.SOSCoeffs)
            # Make sure we have the right number of sections
            self.assertEqual(len(raw_filter_f_fo.coeffs.values), 1)
            self.assertEqual(len(raw_filter_f_fo.coeffs.values[0]), 6)
            # First order filter => b2 == 0 & a2 == 0
            self.assertLess(abs(raw_filter_f_fo.coeffs.values[0][2]), 1e-12)
            self.assertLess(abs(raw_filter_f_fo.coeffs.values[0][5]), 1e-12)

            # filter_d_fo
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawIir)
            raw_filter_d_fo: RawIir = received[1].raw_entities[0]
            self.assertIsInstance(raw_filter_d_fo.coeffs, RawIir.SOSCoeffs)
            # Make sure we have the right number of sections
            self.assertEqual(len(raw_filter_d_fo.coeffs.values), 1)
            self.assertEqual(len(raw_filter_d_fo.coeffs.values[0]), 6)
            # First order filter => b2 == 0 & a2 == 0
            self.assertLess(abs(raw_filter_d_fo.coeffs.values[0][2]), 1e-12)
            self.assertLess(abs(raw_filter_d_fo.coeffs.values[0][5]), 1e-12)

            # filter_f_so
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawIir)
            raw_filter_f_so: RawIir = received[2].raw_entities[0]
            self.assertIsInstance(raw_filter_f_so.coeffs, RawIir.SOSCoeffs)
            # Make sure we have the right number of sections
            self.assertEqual(len(raw_filter_f_so.coeffs.values), 1)
            self.assertEqual(len(raw_filter_f_so.coeffs.values[0]), 6)
            # Second order filter => b2 != 0 || a2 != 0
            try:
                self.assertGreater(abs(raw_filter_f_so.coeffs.values[0][2]), 1e-12)
            except AssertionError:
                self.assertGreater(abs(raw_filter_f_so.coeffs.values[0][5]), 1e-12)

            # filter_d_so
            self.assertEqual(len(received[3].raw_entities), 1)
            self.assertIsInstance(received[3].raw_entities[0], RawIir)
            raw_filter_d_so: RawIir = received[3].raw_entities[0]
            self.assertIsInstance(raw_filter_d_so.coeffs, RawIir.SOSCoeffs)
            # Make sure we have the right number of sections
            self.assertEqual(len(raw_filter_d_so.coeffs.values), 1)
            self.assertEqual(len(raw_filter_d_so.coeffs.values[0]), 6)
            # Second order filter => b2 != 0 || a2 != 0
            try:
                self.assertGreater(abs(raw_filter_d_so.coeffs.values[0][2]), 1e-12)
            except AssertionError:
                self.assertGreater(abs(raw_filter_d_so.coeffs.values[0][5]), 1e-12)

    @patch_client_popen
    def test_iir_svf_old(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("iirSVF", [1, 2, 3])

        ################## iirSVF::1 - Low Pass ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show old_filter_f")
            self.debugger().execute("dave show old_filter_d")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 2, RawEntityList)

            # old_filter_f
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawIir)
            raw_old_filter_f: RawIir = received[0].raw_entities[0]
            self.assertIsInstance(raw_old_filter_f.coeffs, RawIir.SVFTPTCoeffs)
            # check filter type
            self.assertEqual(
                raw_old_filter_f.coeffs.ftype,
                RawIir.SVFTPTCoeffs.FilterType.LP,
            )

            # old_filter_d
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawIir)
            raw_old_filter_d: RawIir = received[1].raw_entities[0]
            self.assertIsInstance(raw_old_filter_d.coeffs, RawIir.SVFTPTCoeffs)
            # check filter type
            self.assertEqual(
                raw_old_filter_d.coeffs.ftype,
                RawIir.SVFTPTCoeffs.FilterType.LP,
            )

        ################## iirSVF::2 - Band Pass ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 2, RawIir.InScopeUpdate)

            # old_filter_f
            self.assertEqual(received[0].id, raw_old_filter_f.id)
            self.assertIsInstance(received[0].coeffs, RawIir.SVFTPTCoeffs)
            # check filter type
            self.assertEqual(
                received[0].coeffs.ftype,
                RawIir.SVFTPTCoeffs.FilterType.BP,
            )

            # old_filter_d
            self.assertEqual(received[1].id, raw_old_filter_d.id)
            self.assertIsInstance(received[1].coeffs, RawIir.SVFTPTCoeffs)
            # check filter type
            self.assertEqual(
                received[1].coeffs.ftype,
                RawIir.SVFTPTCoeffs.FilterType.BP,
            )

        ################## iirSVF::3 - High Pass ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 2, RawIir.InScopeUpdate)

            # old_filter_f
            self.assertEqual(received[0].id, raw_old_filter_f.id)
            self.assertIsInstance(received[0].coeffs, RawIir.SVFTPTCoeffs)
            # check filter type
            self.assertEqual(
                received[0].coeffs.ftype,
                RawIir.SVFTPTCoeffs.FilterType.HP,
            )

            # old_filter_d
            self.assertEqual(received[1].id, raw_old_filter_d.id)
            self.assertIsInstance(received[1].coeffs, RawIir.SVFTPTCoeffs)
            # check filter type
            self.assertEqual(
                received[1].coeffs.ftype,
                RawIir.SVFTPTCoeffs.FilterType.HP,
            )

    @patch_client_popen
    def test_iir_svf(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("iirSVF", [1, 2, 3])

        ################## iirSVF::1 - Low Pass ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show filter_f")
            self.debugger().execute("dave show filter_d")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 2, RawEntityList)

            # filter_f
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawIir)
            raw_filter_f: RawIir = received[0].raw_entities[0]
            self.assertIsInstance(raw_filter_f.coeffs, RawIir.SVFTPTCoeffs)
            # check filter type
            self.assertEqual(
                raw_filter_f.coeffs.ftype,
                RawIir.SVFTPTCoeffs.FilterType.LP,
            )

            # filter_d
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawIir)
            raw_filter_d: RawIir = received[1].raw_entities[0]
            self.assertIsInstance(raw_filter_d.coeffs, RawIir.SVFTPTCoeffs)
            # check filter type
            self.assertEqual(
                raw_filter_d.coeffs.ftype,
                RawIir.SVFTPTCoeffs.FilterType.LP,
            )

        ################## iirSVF::2 - Band Pass ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 2, RawIir.InScopeUpdate)

            # filter_f
            self.assertEqual(received[0].id, raw_filter_f.id)
            self.assertIsInstance(received[0].coeffs, RawIir.SVFTPTCoeffs)
            # check filter type
            self.assertEqual(
                received[0].coeffs.ftype,
                RawIir.SVFTPTCoeffs.FilterType.BP,
            )

            # filter_d
            self.assertEqual(received[1].id, raw_filter_d.id)
            self.assertIsInstance(received[1].coeffs, RawIir.SVFTPTCoeffs)
            # check filter type
            self.assertEqual(
                received[1].coeffs.ftype,
                RawIir.SVFTPTCoeffs.FilterType.BP,
            )

        ################## iirSVF::3 - High Pass ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 2, RawIir.InScopeUpdate)

            # filter_f
            self.assertEqual(received[0].id, raw_filter_f.id)
            self.assertIsInstance(received[0].coeffs, RawIir.SVFTPTCoeffs)
            # check filter type
            self.assertEqual(
                received[0].coeffs.ftype,
                RawIir.SVFTPTCoeffs.FilterType.HP,
            )

            # filter_d
            self.assertEqual(received[1].id, raw_filter_d.id)
            self.assertIsInstance(received[1].coeffs, RawIir.SVFTPTCoeffs)
            # check filter type
            self.assertEqual(
                received[1].coeffs.ftype,
                RawIir.SVFTPTCoeffs.FilterType.HP,
            )
