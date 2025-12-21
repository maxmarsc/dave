from typing import List, Tuple
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
        self.debugger().set_breakpoint("std_tests.cpp:32")
        self.debugger().set_breakpoint("std_tests.cpp:41")

        ################## std_tests.cpp:27 - All zeros ##################
        self.debugger().run()
        self.debugger().execute("dave show array_f")
        self.debugger().execute("dave show array_c")
        self.debugger().execute("dave show array_d")
        self.debugger().execute("dave show array_cd")

        received = MockClient().receive_from_server()
        self.assertIsListOf(received, 4, RawEntityList)

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

        # array_d
        self.assertEqual(len(received[2].raw_entities), 1)
        self.assertIsInstance(received[2].raw_entities[0], RawContainer)
        raw_array_d: RawContainer = received[2].raw_entities[0]
        self.assertArrayInvariants(raw_array_d)
        self.assertTupleEqual(raw_array_d.original_shape, (1, 3))
        self.assertEqual(raw_array_d.sample_type, SampleType.DOUBLE)
        self.assertEqual(raw_array_d.default_layout, RawContainer.Layout.REAL_1D)
        self.assertContainerContent((0.0, 0.0, 0.0), raw_array_d)

        # array_cd
        self.assertEqual(len(received[3].raw_entities), 1)
        self.assertIsInstance(received[3].raw_entities[0], RawContainer)
        raw_array_cd: RawContainer = received[3].raw_entities[0]
        self.assertArrayInvariants(raw_array_cd)
        self.assertTupleEqual(raw_array_cd.original_shape, (1, 3))
        self.assertEqual(raw_array_cd.sample_type, SampleType.CPX_D)
        self.assertEqual(raw_array_cd.default_layout, RawContainer.Layout.CPX_1D)
        self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_array_cd)

        ################## std_tests.cpp:36 - (1, -1, 0) ##################
        self.debugger().continue_()
        received = MockClient().receive_from_server()
        self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

        # array_f
        self.assertEqual(received[0].id, raw_array_f.id)
        self.assertTupleEqual(received[0].shape, raw_array_f.original_shape)
        self.assertContainerContent((1.0, -1.0, 0.0), raw_array_f, received[0])

        # array_c
        self.assertEqual(received[1].id, raw_array_c.id)
        self.assertTupleEqual(received[1].shape, raw_array_c.original_shape)
        self.assertContainerContent((1 + 1j, -1 - 1j, 0 + 0j), raw_array_c, received[1])

        # array_f
        self.assertEqual(received[2].id, raw_array_d.id)
        self.assertTupleEqual(received[2].shape, raw_array_d.original_shape)
        self.assertContainerContent((1.0, -1.0, 0.0), raw_array_d, received[2])

        # array_c
        self.assertEqual(received[3].id, raw_array_cd.id)
        self.assertTupleEqual(received[3].shape, raw_array_cd.original_shape)
        self.assertContainerContent(
            (1 + 1j, -1 - 1j, 0 + 0j), raw_array_cd, received[3]
        )

    @patch_client_popen
    def test_span_static(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoint("std_tests.cpp:32")
        self.debugger().set_breakpoint("std_tests.cpp:41")

        ################## std_tests.cpp:32 - All zeros ##################
        self.debugger().run()
        self.debugger().execute("dave show span_f")
        self.debugger().execute("dave show span_c")
        self.debugger().execute("dave show span_d")
        self.debugger().execute("dave show span_cd")

        received = MockClient().receive_from_server()
        self.assertIsListOf(received, 4, RawEntityList)

        # array_f
        self.assertEqual(len(received[0].raw_entities), 1)
        self.assertIsInstance(received[0].raw_entities[0], RawContainer)
        raw_span_f: RawContainer = received[0].raw_entities[0]
        self.assertArrayInvariants(raw_span_f)
        self.assertTupleEqual(raw_span_f.original_shape, (1, 3))
        self.assertEqual(raw_span_f.sample_type, SampleType.FLOAT)
        self.assertEqual(raw_span_f.default_layout, RawContainer.Layout.REAL_1D)
        self.assertContainerContent((0.0, 0.0, 0.0), raw_span_f)

        # array_c
        self.assertEqual(len(received[1].raw_entities), 1)
        self.assertIsInstance(received[1].raw_entities[0], RawContainer)
        raw_span_c: RawContainer = received[1].raw_entities[0]
        self.assertArrayInvariants(raw_span_c)
        self.assertTupleEqual(raw_span_c.original_shape, (1, 3))
        self.assertEqual(raw_span_c.sample_type, SampleType.CPX_F)
        self.assertEqual(raw_span_c.default_layout, RawContainer.Layout.CPX_1D)
        self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_span_c)

        # array_d
        self.assertEqual(len(received[2].raw_entities), 1)
        self.assertIsInstance(received[2].raw_entities[0], RawContainer)
        raw_span_d: RawContainer = received[2].raw_entities[0]
        self.assertArrayInvariants(raw_span_d)
        self.assertTupleEqual(raw_span_d.original_shape, (1, 3))
        self.assertEqual(raw_span_d.sample_type, SampleType.DOUBLE)
        self.assertEqual(raw_span_d.default_layout, RawContainer.Layout.REAL_1D)
        self.assertContainerContent((0.0, 0.0, 0.0), raw_span_d)

        # array_cd
        self.assertEqual(len(received[3].raw_entities), 1)
        self.assertIsInstance(received[3].raw_entities[0], RawContainer)
        raw_span_cd: RawContainer = received[3].raw_entities[0]
        self.assertArrayInvariants(raw_span_cd)
        self.assertTupleEqual(raw_span_cd.original_shape, (1, 3))
        self.assertEqual(raw_span_cd.sample_type, SampleType.CPX_D)
        self.assertEqual(raw_span_cd.default_layout, RawContainer.Layout.CPX_1D)
        self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_span_cd)

        ################## std_tests.cpp:36 - (1, -1, 0) ##################
        self.debugger().continue_()
        received = MockClient().receive_from_server()
        self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

        # array_f
        self.assertEqual(received[0].id, raw_span_f.id)
        self.assertTupleEqual(received[0].shape, raw_span_f.original_shape)
        self.assertContainerContent((1.0, -1.0, 0.0), raw_span_f, received[0])

        # array_c
        self.assertEqual(received[1].id, raw_span_c.id)
        self.assertTupleEqual(received[1].shape, raw_span_c.original_shape)
        self.assertContainerContent((1 + 1j, -1 - 1j, 0 + 0j), raw_span_c, received[1])

        # array_f
        self.assertEqual(received[2].id, raw_span_d.id)
        self.assertTupleEqual(received[2].shape, raw_span_d.original_shape)
        self.assertContainerContent((1.0, -1.0, 0.0), raw_span_d, received[2])

        # array_c
        self.assertEqual(received[3].id, raw_span_cd.id)
        self.assertTupleEqual(received[3].shape, raw_span_cd.original_shape)
        self.assertContainerContent((1 + 1j, -1 - 1j, 0 + 0j), raw_span_cd, received[3])

    @patch_client_popen
    def test_c_array(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoint("std_tests.cpp:51")
        self.debugger().set_breakpoint("std_tests.cpp:60")

        ################## std_tests.cpp:46 - All zeros ##################
        self.debugger().run()
        self.debugger().execute("dave show array_f")
        self.debugger().execute("dave show array_c")
        self.debugger().execute("dave show array_d")
        self.debugger().execute("dave show array_cd")

        received = MockClient().receive_from_server()
        self.assertIsListOf(received, 4, RawEntityList)

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

        # array_d
        self.assertEqual(len(received[2].raw_entities), 1)
        self.assertIsInstance(received[2].raw_entities[0], RawContainer)
        raw_array_d: RawContainer = received[2].raw_entities[0]
        self.assertArrayInvariants(raw_array_d)
        self.assertTupleEqual(raw_array_d.original_shape, (1, 3))
        self.assertEqual(raw_array_d.sample_type, SampleType.DOUBLE)
        self.assertEqual(raw_array_d.default_layout, RawContainer.Layout.REAL_1D)
        self.assertContainerContent((0.0, 0.0, 0.0), raw_array_d)

        # array_cd
        self.assertEqual(len(received[3].raw_entities), 1)
        self.assertIsInstance(received[3].raw_entities[0], RawContainer)
        raw_array_cd: RawContainer = received[3].raw_entities[0]
        self.assertArrayInvariants(raw_array_cd)
        self.assertTupleEqual(raw_array_cd.original_shape, (1, 3))
        self.assertEqual(raw_array_cd.sample_type, SampleType.CPX_D)
        self.assertEqual(raw_array_cd.default_layout, RawContainer.Layout.CPX_1D)
        self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_array_cd)

        ################## std_tests.cpp:55 - (1, -1, 0) ##################
        self.debugger().continue_()
        received = MockClient().receive_from_server()
        self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

        # array_f
        self.assertEqual(received[0].id, raw_array_f.id)
        self.assertTupleEqual(received[0].shape, raw_array_f.original_shape)
        self.assertContainerContent((1.0, -1.0, 0.0), raw_array_f, received[0])

        # array_c
        self.assertEqual(received[1].id, raw_array_c.id)
        self.assertTupleEqual(received[1].shape, raw_array_c.original_shape)
        self.assertContainerContent((1 + 1j, -1 - 1j, 0 + 0j), raw_array_c, received[1])

        # array_f
        self.assertEqual(received[2].id, raw_array_d.id)
        self.assertTupleEqual(received[2].shape, raw_array_d.original_shape)
        self.assertContainerContent((1.0, -1.0, 0.0), raw_array_d, received[2])

        # array_c
        self.assertEqual(received[3].id, raw_array_cd.id)
        self.assertTupleEqual(received[3].shape, raw_array_cd.original_shape)
        self.assertContainerContent(
            (1 + 1j, -1 - 1j, 0 + 0j), raw_array_cd, received[3]
        )

    @patch_client_popen
    def test_vector(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoint("std_tests.cpp:98")
        self.debugger().set_breakpoint("std_tests.cpp:107")
        self.debugger().set_breakpoint("std_tests.cpp:116")
        self.debugger().set_breakpoint("std_tests.cpp:125")

        ################## std_tests.cpp:99 - All zeros ##################
        self.debugger().run()
        self.debugger().execute("dave show vector_f")
        self.debugger().execute("dave show vector_c")
        self.debugger().execute("dave show vector_d")
        self.debugger().execute("dave show vector_cd")

        received = MockClient().receive_from_server()
        self.assertIsListOf(received, 4, RawEntityList)

        # vector_f
        self.assertEqual(len(received[0].raw_entities), 1)
        self.assertIsInstance(received[0].raw_entities[0], RawContainer)
        raw_vector_f: RawContainer = received[0].raw_entities[0]
        self.assertArrayInvariants(raw_vector_f)
        self.assertTupleEqual(raw_vector_f.original_shape, (1, 3))
        self.assertEqual(raw_vector_f.sample_type, SampleType.FLOAT)
        self.assertEqual(raw_vector_f.default_layout, RawContainer.Layout.REAL_1D)
        self.assertContainerContent((0.0, 0.0, 0.0), raw_vector_f)

        # vector_c
        self.assertEqual(len(received[1].raw_entities), 1)
        self.assertIsInstance(received[1].raw_entities[0], RawContainer)
        raw_vector_c: RawContainer = received[1].raw_entities[0]
        self.assertArrayInvariants(raw_vector_c)
        self.assertTupleEqual(raw_vector_c.original_shape, (1, 3))
        self.assertEqual(raw_vector_c.sample_type, SampleType.CPX_F)
        self.assertEqual(raw_vector_c.default_layout, RawContainer.Layout.CPX_1D)
        self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_vector_c)

        # vector_d
        self.assertEqual(len(received[2].raw_entities), 1)
        self.assertIsInstance(received[2].raw_entities[0], RawContainer)
        raw_vector_d: RawContainer = received[2].raw_entities[0]
        self.assertArrayInvariants(raw_vector_d)
        self.assertTupleEqual(raw_vector_d.original_shape, (1, 3))
        self.assertEqual(raw_vector_d.sample_type, SampleType.DOUBLE)
        self.assertEqual(raw_vector_d.default_layout, RawContainer.Layout.REAL_1D)
        self.assertContainerContent((0.0, 0.0, 0.0), raw_vector_d)

        # vector_cd
        self.assertEqual(len(received[3].raw_entities), 1)
        self.assertIsInstance(received[3].raw_entities[0], RawContainer)
        raw_vector_cd: RawContainer = received[3].raw_entities[0]
        self.assertArrayInvariants(raw_vector_cd)
        self.assertTupleEqual(raw_vector_cd.original_shape, (1, 3))
        self.assertEqual(raw_vector_cd.sample_type, SampleType.CPX_D)
        self.assertEqual(raw_vector_cd.default_layout, RawContainer.Layout.CPX_1D)
        self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_vector_cd)

        ################## std_tests.cpp:107 - (1, -1, 0) ##################
        self.debugger().continue_()
        received = MockClient().receive_from_server()
        self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

        # array_f
        self.assertEqual(received[0].id, raw_vector_f.id)
        self.assertTupleEqual(received[0].shape, raw_vector_f.original_shape)
        self.assertContainerContent((1.0, -1.0, 0.0), raw_vector_f, received[0])

        # array_c
        self.assertEqual(received[1].id, raw_vector_c.id)
        self.assertTupleEqual(received[1].shape, raw_vector_c.original_shape)
        self.assertContainerContent(
            (1 + 1j, -1 - 1j, 0 + 0j), raw_vector_c, received[1]
        )

        # array_f
        self.assertEqual(received[2].id, raw_vector_d.id)
        self.assertTupleEqual(received[2].shape, raw_vector_d.original_shape)
        self.assertContainerContent((1.0, -1.0, 0.0), raw_vector_d, received[2])

        # array_c
        self.assertEqual(received[3].id, raw_vector_cd.id)
        self.assertTupleEqual(received[3].shape, raw_vector_cd.original_shape)
        self.assertContainerContent(
            (1 + 1j, -1 - 1j, 0 + 0j), raw_vector_cd, received[3]
        )
