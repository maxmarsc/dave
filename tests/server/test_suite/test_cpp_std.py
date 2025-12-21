from typing import Tuple
import struct

from common import TestCaseBase, C_CPP_BUILD_DIR
from mocked import MockClient, patch_client_popen

from dave.common.raw_entity import RawEntity, RawEntityList, RawEntityUpdates
from dave.common.raw_container import RawContainer
from dave.common.sample_type import SampleType

CONTAINER_1D_LAYOUTS = [
    RawContainer.Layout.CPX_1D,
    RawContainer.Layout.CPX_2D,
    RawContainer.Layout.REAL_1D,
    RawContainer.Layout.REAL_2D,
]

NAN = float("nan")


class TestCppStd(TestCaseBase.TYPE):
    BINARY = C_CPP_BUILD_DIR / "std_tests"
    BINARY_HASH = "hihou"

    def assertArrayInvariants(self, array: RawContainer):
        self.assertListEqual(array.possible_layout, CONTAINER_1D_LAYOUTS)
        self.assertEqual(array.dimensions_fixed, False)
        self.assertEqual(array.interleaved, False)

    @patch_client_popen
    def test_array(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoint("std_tests.cpp:28")
        self.debugger().set_breakpoint("std_tests.cpp:34")
        self.debugger().set_breakpoint("std_tests.cpp:40")
        self.debugger().set_breakpoint("std_tests.cpp:54")

        ################## std_tests.cpp:28 - All zeros ##################
        self.debugger().run()
        self.debugger().execute("dave show array_f")
        self.debugger().execute("dave show array_c")
        received = MockClient().receive_from_server()
        self.assertIsListOf(received, 2, RawEntityList)

        # array_f
        self.assertEqual(len(received[0].raw_entities), 1)
        self.assertIsInstance(received[0].raw_entities[0], RawContainer)
        raw_array_f: RawContainer = received[0].raw_entities[0]
        self.assertArrayInvariants(raw_array_f)
        self.assertTupleEqual(raw_array_f.original_shape, (1, 3))
        self.assertEqual(raw_array_f.sample_type, SampleType.FLOAT)
        self.assertEqual(raw_array_f.default_layout, RawContainer.Layout.REAL_1D)
        self.assertContainerContent((0.0, 0.0, 0.0), raw_array_f)

        # array_c
        self.assertEqual(len(received[1].raw_entities), 1)
        self.assertIsInstance(received[1].raw_entities[0], RawContainer)
        raw_array_c: RawContainer = received[1].raw_entities[0]
        self.assertArrayInvariants(raw_array_c)
        self.assertTupleEqual(raw_array_c.original_shape, (1, 3))
        self.assertEqual(raw_array_c.sample_type, SampleType.CPX_F)
        self.assertEqual(raw_array_c.default_layout, RawContainer.Layout.CPX_1D)
        self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_array_c)

        ################## std_tests.cpp:34 - (1, 0, 0) ##################
        self.debugger().continue_()
        received = MockClient().receive_from_server()
        self.assertIsListOf(received, 2, RawContainer.InScopeUpdate)

        # array_f
        self.assertEqual(received[0].id, raw_array_f.id)
        self.assertTupleEqual(received[0].shape, raw_array_f.original_shape)
        self.assertContainerContent((1.0, 0.0, 0.0), raw_array_f, received[0])

        # array_c
        self.assertEqual(received[1].id, raw_array_c.id)
        self.assertTupleEqual(received[1].shape, raw_array_c.original_shape)
        self.assertContainerContent((1 + 1j, 0 + 0j, 0 + 0j), raw_array_c, received[1])
