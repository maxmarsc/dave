from common import TestCaseBase, C_CPP_BUILD_DIR
from mocked import MockClient, patch_client_popen

from dave.common.raw_entity import RawEntityList
from dave.common.raw_container import RawContainer
from dave.common.sample_type import SampleType

CONTAINER_1D_LAYOUTS = [
    RawContainer.Layout.CPX_1D,
    RawContainer.Layout.CPX_2D,
    RawContainer.Layout.REAL_1D,
    RawContainer.Layout.REAL_2D,
]
CONTAINER_2D_LAYOUTS = [
    RawContainer.Layout.CPX_2D,
    RawContainer.Layout.REAL_2D,
]


class TestCppStd(TestCaseBase.TYPE):
    BINARY = C_CPP_BUILD_DIR / "std_tests"

    def assertContainer1DInvariants(self, array: RawContainer):
        self.assertListEqual(array.possible_layout, CONTAINER_1D_LAYOUTS)
        self.assertEqual(array.dimensions_fixed, False)
        self.assertEqual(array.interleaved, False)

    def assertContainer2DInvariants(self, array: RawContainer):
        self.assertListEqual(array.possible_layout, CONTAINER_2D_LAYOUTS)
        self.assertEqual(array.dimensions_fixed, True)
        self.assertEqual(array.interleaved, False)

    @patch_client_popen
    def test_array(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("arrayAndStaticSpan", [1, 2])

        ################## arrayAndStaticSpan::1 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
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
            self.assertContainer1DInvariants(raw_array_f)
            self.assertTupleEqual(raw_array_f.original_shape, (1, 3))
            self.assertEqual(raw_array_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_array_f.default_layout, RawContainer.Layout.REAL_1D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_array_f)

            # array_c
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_array_c: RawContainer = received[1].raw_entities[0]
            self.assertContainer1DInvariants(raw_array_c)
            self.assertTupleEqual(raw_array_c.original_shape, (1, 3))
            self.assertEqual(raw_array_c.sample_type, SampleType.CPX_F)
            self.assertEqual(raw_array_c.default_layout, RawContainer.Layout.CPX_1D)
            self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_array_c)

            # array_d
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawContainer)
            raw_array_d: RawContainer = received[2].raw_entities[0]
            self.assertContainer1DInvariants(raw_array_d)
            self.assertTupleEqual(raw_array_d.original_shape, (1, 3))
            self.assertEqual(raw_array_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(raw_array_d.default_layout, RawContainer.Layout.REAL_1D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_array_d)

            # array_cd
            self.assertEqual(len(received[3].raw_entities), 1)
            self.assertIsInstance(received[3].raw_entities[0], RawContainer)
            raw_array_cd: RawContainer = received[3].raw_entities[0]
            self.assertContainer1DInvariants(raw_array_cd)
            self.assertTupleEqual(raw_array_cd.original_shape, (1, 3))
            self.assertEqual(raw_array_cd.sample_type, SampleType.CPX_D)
            self.assertEqual(raw_array_cd.default_layout, RawContainer.Layout.CPX_1D)
            self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_array_cd)

        ################## arrayAndStaticSpan::2 - (1, -1, 0) ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # array_f
            self.assertEqual(received[0].id, raw_array_f.id)
            self.assertTupleEqual(received[0].shape, raw_array_f.original_shape)
            self.assertContainerContent((1.0, -1.0, 0.0), raw_array_f, received[0])

            # array_c
            self.assertEqual(received[1].id, raw_array_c.id)
            self.assertTupleEqual(received[1].shape, raw_array_c.original_shape)
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0 + 0j), raw_array_c, received[1]
            )

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
        self.debugger().set_breakpoints_at_tags("arrayAndStaticSpan", [1, 2])

        ################## arrayAndStaticSpan::1 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
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
            self.assertContainer1DInvariants(raw_span_f)
            self.assertTupleEqual(raw_span_f.original_shape, (1, 3))
            self.assertEqual(raw_span_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_span_f.default_layout, RawContainer.Layout.REAL_1D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_span_f)

            # array_c
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_span_c: RawContainer = received[1].raw_entities[0]
            self.assertContainer1DInvariants(raw_span_c)
            self.assertTupleEqual(raw_span_c.original_shape, (1, 3))
            self.assertEqual(raw_span_c.sample_type, SampleType.CPX_F)
            self.assertEqual(raw_span_c.default_layout, RawContainer.Layout.CPX_1D)
            self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_span_c)

            # array_d
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawContainer)
            raw_span_d: RawContainer = received[2].raw_entities[0]
            self.assertContainer1DInvariants(raw_span_d)
            self.assertTupleEqual(raw_span_d.original_shape, (1, 3))
            self.assertEqual(raw_span_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(raw_span_d.default_layout, RawContainer.Layout.REAL_1D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_span_d)

            # array_cd
            self.assertEqual(len(received[3].raw_entities), 1)
            self.assertIsInstance(received[3].raw_entities[0], RawContainer)
            raw_span_cd: RawContainer = received[3].raw_entities[0]
            self.assertContainer1DInvariants(raw_span_cd)
            self.assertTupleEqual(raw_span_cd.original_shape, (1, 3))
            self.assertEqual(raw_span_cd.sample_type, SampleType.CPX_D)
            self.assertEqual(raw_span_cd.default_layout, RawContainer.Layout.CPX_1D)
            self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_span_cd)

        ################## arrayAndStaticSpan::2 - (1, -1, 0) ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # array_f
            self.assertEqual(received[0].id, raw_span_f.id)
            self.assertTupleEqual(received[0].shape, raw_span_f.original_shape)
            self.assertContainerContent((1.0, -1.0, 0.0), raw_span_f, received[0])

            # array_c
            self.assertEqual(received[1].id, raw_span_c.id)
            self.assertTupleEqual(received[1].shape, raw_span_c.original_shape)
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0 + 0j), raw_span_c, received[1]
            )

            # array_f
            self.assertEqual(received[2].id, raw_span_d.id)
            self.assertTupleEqual(received[2].shape, raw_span_d.original_shape)
            self.assertContainerContent((1.0, -1.0, 0.0), raw_span_d, received[2])

            # array_c
            self.assertEqual(received[3].id, raw_span_cd.id)
            self.assertTupleEqual(received[3].shape, raw_span_cd.original_shape)
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0 + 0j), raw_span_cd, received[3]
            )

    @patch_client_popen
    def test_c_array(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("cArrayAndPtr", [1, 2])

        ################## cArrayAndPtr::1 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
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
            self.assertContainer1DInvariants(raw_array_f)
            self.assertTupleEqual(raw_array_f.original_shape, (1, 3))
            self.assertEqual(raw_array_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_array_f.default_layout, RawContainer.Layout.REAL_1D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_array_f)

            # array_c
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_array_c: RawContainer = received[1].raw_entities[0]
            self.assertContainer1DInvariants(raw_array_c)
            self.assertTupleEqual(raw_array_c.original_shape, (1, 3))
            self.assertEqual(raw_array_c.sample_type, SampleType.CPX_F)
            self.assertEqual(raw_array_c.default_layout, RawContainer.Layout.CPX_1D)
            self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_array_c)

            # array_d
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawContainer)
            raw_array_d: RawContainer = received[2].raw_entities[0]
            self.assertContainer1DInvariants(raw_array_d)
            self.assertTupleEqual(raw_array_d.original_shape, (1, 3))
            self.assertEqual(raw_array_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(raw_array_d.default_layout, RawContainer.Layout.REAL_1D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_array_d)

            # array_cd
            self.assertEqual(len(received[3].raw_entities), 1)
            self.assertIsInstance(received[3].raw_entities[0], RawContainer)
            raw_array_cd: RawContainer = received[3].raw_entities[0]
            self.assertContainer1DInvariants(raw_array_cd)
            self.assertTupleEqual(raw_array_cd.original_shape, (1, 3))
            self.assertEqual(raw_array_cd.sample_type, SampleType.CPX_D)
            self.assertEqual(raw_array_cd.default_layout, RawContainer.Layout.CPX_1D)
            self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_array_cd)

        ################## cArrayAndPtr::2 - (1, -1, 0) ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # array_f
            self.assertEqual(received[0].id, raw_array_f.id)
            self.assertTupleEqual(received[0].shape, raw_array_f.original_shape)
            self.assertContainerContent((1.0, -1.0, 0.0), raw_array_f, received[0])

            # array_c
            self.assertEqual(received[1].id, raw_array_c.id)
            self.assertTupleEqual(received[1].shape, raw_array_c.original_shape)
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0 + 0j), raw_array_c, received[1]
            )

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
    def test_pointer(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("cArrayAndPtr", [1, 2])

        ################## cArrayAndPtr::1 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show ptr_f --dims 3")
            self.debugger().execute("dave show ptr_c --dims 3")
            self.debugger().execute("dave show ptr_d --dims 3")
            self.debugger().execute("dave show ptr_cd --dims 3")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawEntityList)

            # ptr_f
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            raw_ptr_f: RawContainer = received[0].raw_entities[0]
            self.assertContainer1DInvariants(raw_ptr_f)
            self.assertTupleEqual(raw_ptr_f.original_shape, (1, 3))
            self.assertEqual(raw_ptr_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_ptr_f.default_layout, RawContainer.Layout.REAL_1D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_ptr_f)

            # ptr_c
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_ptr_c: RawContainer = received[1].raw_entities[0]
            self.assertContainer1DInvariants(raw_ptr_c)
            self.assertTupleEqual(raw_ptr_c.original_shape, (1, 3))
            self.assertEqual(raw_ptr_c.sample_type, SampleType.CPX_F)
            self.assertEqual(raw_ptr_c.default_layout, RawContainer.Layout.CPX_1D)
            self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_ptr_c)

            # ptr_d
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawContainer)
            raw_ptr_d: RawContainer = received[2].raw_entities[0]
            self.assertContainer1DInvariants(raw_ptr_d)
            self.assertTupleEqual(raw_ptr_d.original_shape, (1, 3))
            self.assertEqual(raw_ptr_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(raw_ptr_d.default_layout, RawContainer.Layout.REAL_1D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_ptr_d)

            # ptr_cd
            self.assertEqual(len(received[3].raw_entities), 1)
            self.assertIsInstance(received[3].raw_entities[0], RawContainer)
            raw_ptr_cd: RawContainer = received[3].raw_entities[0]
            self.assertContainer1DInvariants(raw_ptr_cd)
            self.assertTupleEqual(raw_ptr_cd.original_shape, (1, 3))
            self.assertEqual(raw_ptr_cd.sample_type, SampleType.CPX_D)
            self.assertEqual(raw_ptr_cd.default_layout, RawContainer.Layout.CPX_1D)
            self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_ptr_cd)

        ################## cArrayAndPtr::2 - (1, -1, 0) ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # ptr_f
            self.assertEqual(received[0].id, raw_ptr_f.id)
            self.assertTupleEqual(received[0].shape, raw_ptr_f.original_shape)
            self.assertContainerContent((1.0, -1.0, 0.0), raw_ptr_f, received[0])

            # ptr_c
            self.assertEqual(received[1].id, raw_ptr_c.id)
            self.assertTupleEqual(received[1].shape, raw_ptr_c.original_shape)
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0 + 0j), raw_ptr_c, received[1]
            )

            # ptr_f
            self.assertEqual(received[2].id, raw_ptr_d.id)
            self.assertTupleEqual(received[2].shape, raw_ptr_d.original_shape)
            self.assertContainerContent((1.0, -1.0, 0.0), raw_ptr_d, received[2])

            # ptr_c
            self.assertEqual(received[3].id, raw_ptr_cd.id)
            self.assertTupleEqual(received[3].shape, raw_ptr_cd.original_shape)
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0 + 0j), raw_ptr_cd, received[3]
            )

    @patch_client_popen
    def test_vector(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("vectorAndDynSpan", [1, 2, 3, 4])

        ################## vectorAndDynSpan::1 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
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
            self.assertContainer1DInvariants(raw_vector_f)
            self.assertTupleEqual(raw_vector_f.original_shape, (1, 3))
            self.assertEqual(raw_vector_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_vector_f.default_layout, RawContainer.Layout.REAL_1D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_vector_f)

            # vector_c
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_vector_c: RawContainer = received[1].raw_entities[0]
            self.assertContainer1DInvariants(raw_vector_c)
            self.assertTupleEqual(raw_vector_c.original_shape, (1, 3))
            self.assertEqual(raw_vector_c.sample_type, SampleType.CPX_F)
            self.assertEqual(raw_vector_c.default_layout, RawContainer.Layout.CPX_1D)
            self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_vector_c)

            # vector_d
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawContainer)
            raw_vector_d: RawContainer = received[2].raw_entities[0]
            self.assertContainer1DInvariants(raw_vector_d)
            self.assertTupleEqual(raw_vector_d.original_shape, (1, 3))
            self.assertEqual(raw_vector_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(raw_vector_d.default_layout, RawContainer.Layout.REAL_1D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_vector_d)

            # vector_cd
            self.assertEqual(len(received[3].raw_entities), 1)
            self.assertIsInstance(received[3].raw_entities[0], RawContainer)
            raw_vector_cd: RawContainer = received[3].raw_entities[0]
            self.assertContainer1DInvariants(raw_vector_cd)
            self.assertTupleEqual(raw_vector_cd.original_shape, (1, 3))
            self.assertEqual(raw_vector_cd.sample_type, SampleType.CPX_D)
            self.assertEqual(raw_vector_cd.default_layout, RawContainer.Layout.CPX_1D)
            self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_vector_cd)

        ################## vectorAndDynSpan::2 - (1, -1, 0) ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # vector_f
            self.assertEqual(received[0].id, raw_vector_f.id)
            self.assertTupleEqual(received[0].shape, raw_vector_f.original_shape)
            self.assertContainerContent((1.0, -1.0, 0.0), raw_vector_f, received[0])

            # vector_c
            self.assertEqual(received[1].id, raw_vector_c.id)
            self.assertTupleEqual(received[1].shape, raw_vector_c.original_shape)
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0 + 0j), raw_vector_c, received[1]
            )

            # vector_f
            self.assertEqual(received[2].id, raw_vector_d.id)
            self.assertTupleEqual(received[2].shape, raw_vector_d.original_shape)
            self.assertContainerContent((1.0, -1.0, 0.0), raw_vector_d, received[2])

            # vector_c
            self.assertEqual(received[3].id, raw_vector_cd.id)
            self.assertTupleEqual(received[3].shape, raw_vector_cd.original_shape)
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0 + 0j), raw_vector_cd, received[3]
            )

        ################## vectorAndDynSpan::3 - (1, -1) ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # vector_f
            self.assertEqual(received[0].id, raw_vector_f.id)
            self.assertTupleEqual(received[0].shape, (1, 2))
            self.assertContainerContent((1.0, -1.0), raw_vector_f, received[0])

            # vector_c
            self.assertEqual(received[1].id, raw_vector_c.id)
            self.assertTupleEqual(received[1].shape, (1, 2))
            self.assertContainerContent((1 + 1j, -1 - 1j), raw_vector_c, received[1])

            # vector_f
            self.assertEqual(received[2].id, raw_vector_d.id)
            self.assertTupleEqual(received[2].shape, (1, 2))
            self.assertContainerContent((1.0, -1.0), raw_vector_d, received[2])

            # vector_c
            self.assertEqual(received[3].id, raw_vector_cd.id)
            self.assertTupleEqual(received[3].shape, (1, 2))
            self.assertContainerContent((1 + 1j, -1 - 1j), raw_vector_cd, received[3])

        ################## vectorAndDynSpan::3 - (1, -1, 0, 0) ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # vector_f
            self.assertEqual(received[0].id, raw_vector_f.id)
            self.assertTupleEqual(received[0].shape, (1, 4))
            self.assertContainerContent(
                (1.0, -1.0, 0.0, 0.0), raw_vector_f, received[0]
            )

            # vector_c
            self.assertEqual(received[1].id, raw_vector_c.id)
            self.assertTupleEqual(received[1].shape, (1, 4))
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0j, 0j), raw_vector_c, received[1]
            )

            # vector_f
            self.assertEqual(received[2].id, raw_vector_d.id)
            self.assertTupleEqual(received[2].shape, (1, 4))
            self.assertContainerContent(
                (1.0, -1.0, 0.0, 0.0), raw_vector_d, received[2]
            )

            # vector_c
            self.assertEqual(received[3].id, raw_vector_cd.id)
            self.assertTupleEqual(received[3].shape, (1, 4))
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0j, 0j), raw_vector_cd, received[3]
            )

    @patch_client_popen
    def test_span_dyn(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("vectorAndDynSpan", [1, 2, 3, 4])

        ################## vectorAndDynSpan::1 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show span_f")
            self.debugger().execute("dave show span_c")
            self.debugger().execute("dave show span_d")
            self.debugger().execute("dave show span_cd")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawEntityList)

            # span_f
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            raw_span_f: RawContainer = received[0].raw_entities[0]
            self.assertContainer1DInvariants(raw_span_f)
            self.assertTupleEqual(raw_span_f.original_shape, (1, 3))
            self.assertEqual(raw_span_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_span_f.default_layout, RawContainer.Layout.REAL_1D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_span_f)

            # span_c
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_span_c: RawContainer = received[1].raw_entities[0]
            self.assertContainer1DInvariants(raw_span_c)
            self.assertTupleEqual(raw_span_c.original_shape, (1, 3))
            self.assertEqual(raw_span_c.sample_type, SampleType.CPX_F)
            self.assertEqual(raw_span_c.default_layout, RawContainer.Layout.CPX_1D)
            self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_span_c)

            # span_d
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawContainer)
            raw_span_d: RawContainer = received[2].raw_entities[0]
            self.assertContainer1DInvariants(raw_span_d)
            self.assertTupleEqual(raw_span_d.original_shape, (1, 3))
            self.assertEqual(raw_span_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(raw_span_d.default_layout, RawContainer.Layout.REAL_1D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_span_d)

            # span_cd
            self.assertEqual(len(received[3].raw_entities), 1)
            self.assertIsInstance(received[3].raw_entities[0], RawContainer)
            raw_span_cd: RawContainer = received[3].raw_entities[0]
            self.assertContainer1DInvariants(raw_span_cd)
            self.assertTupleEqual(raw_span_cd.original_shape, (1, 3))
            self.assertEqual(raw_span_cd.sample_type, SampleType.CPX_D)
            self.assertEqual(raw_span_cd.default_layout, RawContainer.Layout.CPX_1D)
            self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_span_cd)

        ################## vectorAndDynSpan::2 - (1, -1, 0) ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # span_f
            self.assertEqual(received[0].id, raw_span_f.id)
            self.assertTupleEqual(received[0].shape, raw_span_f.original_shape)
            self.assertContainerContent((1.0, -1.0, 0.0), raw_span_f, received[0])

            # span_c
            self.assertEqual(received[1].id, raw_span_c.id)
            self.assertTupleEqual(received[1].shape, raw_span_c.original_shape)
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0 + 0j), raw_span_c, received[1]
            )

            # span_f
            self.assertEqual(received[2].id, raw_span_d.id)
            self.assertTupleEqual(received[2].shape, raw_span_d.original_shape)
            self.assertContainerContent((1.0, -1.0, 0.0), raw_span_d, received[2])

            # span_c
            self.assertEqual(received[3].id, raw_span_cd.id)
            self.assertTupleEqual(received[3].shape, raw_span_cd.original_shape)
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0 + 0j), raw_span_cd, received[3]
            )

        ################## vectorAndDynSpan::3 - (1, -1) ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # span_f
            self.assertEqual(received[0].id, raw_span_f.id)
            self.assertTupleEqual(received[0].shape, (1, 2))
            self.assertContainerContent((1.0, -1.0), raw_span_f, received[0])

            # span_c
            self.assertEqual(received[1].id, raw_span_c.id)
            self.assertTupleEqual(received[1].shape, (1, 2))
            self.assertContainerContent((1 + 1j, -1 - 1j), raw_span_c, received[1])

            # span_f
            self.assertEqual(received[2].id, raw_span_d.id)
            self.assertTupleEqual(received[2].shape, (1, 2))
            self.assertContainerContent((1.0, -1.0), raw_span_d, received[2])

            # span_c
            self.assertEqual(received[3].id, raw_span_cd.id)
            self.assertTupleEqual(received[3].shape, (1, 2))
            self.assertContainerContent((1 + 1j, -1 - 1j), raw_span_cd, received[3])

        ################## vectorAndDynSpan::4 - (1, -1, 0, 0) ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # span_f
            self.assertEqual(received[0].id, raw_span_f.id)
            self.assertTupleEqual(received[0].shape, (1, 4))
            self.assertContainerContent((1.0, -1.0, 0.0, 0.0), raw_span_f, received[0])

            # span_c
            self.assertEqual(received[1].id, raw_span_c.id)
            self.assertTupleEqual(received[1].shape, (1, 4))
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0j, 0j), raw_span_c, received[1]
            )

            # span_f
            self.assertEqual(received[2].id, raw_span_d.id)
            self.assertTupleEqual(received[2].shape, (1, 4))
            self.assertContainerContent((1.0, -1.0, 0.0, 0.0), raw_span_d, received[2])

            # span_c
            self.assertEqual(received[3].id, raw_span_cd.id)
            self.assertTupleEqual(received[3].shape, (1, 4))
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0j, 0j), raw_span_cd, received[3]
            )

    @patch_client_popen
    def test_carray_2d(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("cArrayAndPtr2D", [1, 2])

        ################## cArray2D::1 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show array_array_f")
            self.debugger().execute("dave show array_array_d")
            self.debugger().execute("dave show array_ptrs_f --dims 3")
            self.debugger().execute("dave show array_ptrs_d --dims 3")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawEntityList)

            # array_array_f
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            raw_array_array_f: RawContainer = received[0].raw_entities[0]
            self.assertContainer2DInvariants(raw_array_array_f)
            self.assertTupleEqual(raw_array_array_f.original_shape, (2, 3))
            self.assertEqual(raw_array_array_f.sample_type, SampleType.FLOAT)
            self.assertEqual(
                raw_array_array_f.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_array_array_f
            )

            # array_array_d
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_array_array_d: RawContainer = received[1].raw_entities[0]
            self.assertContainer2DInvariants(raw_array_array_d)
            self.assertTupleEqual(raw_array_array_d.original_shape, (2, 3))
            self.assertEqual(raw_array_array_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(
                raw_array_array_d.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_array_array_d
            )

            # array_ptrs_f
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawContainer)
            raw_array_ptrs_f: RawContainer = received[2].raw_entities[0]
            self.assertContainer2DInvariants(raw_array_ptrs_f)
            self.assertTupleEqual(raw_array_ptrs_f.original_shape, (2, 3))
            self.assertEqual(raw_array_ptrs_f.sample_type, SampleType.FLOAT)
            self.assertEqual(
                raw_array_ptrs_f.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_array_ptrs_f
            )

            # array_ptrs_d
            self.assertEqual(len(received[3].raw_entities), 1)
            self.assertIsInstance(received[3].raw_entities[0], RawContainer)
            raw_array_ptrs_d: RawContainer = received[3].raw_entities[0]
            self.assertContainer2DInvariants(raw_array_ptrs_d)
            self.assertTupleEqual(raw_array_ptrs_d.original_shape, (2, 3))
            self.assertEqual(raw_array_ptrs_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(
                raw_array_ptrs_d.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_array_ptrs_d
            )

        ############# cArrayAndPtr2D::2 - (0, 0, 0, 1, -1, 0) ############
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # array_array_f
            self.assertEqual(received[0].id, raw_array_array_f.id)
            self.assertTupleEqual(received[0].shape, raw_array_array_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_array_array_f,
                received[0],
            )

            # array_array_d
            self.assertEqual(received[1].id, raw_array_array_d.id)
            self.assertTupleEqual(received[1].shape, raw_array_array_d.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_array_array_d,
                received[1],
            )

            # array_ptrs_f
            self.assertEqual(received[2].id, raw_array_ptrs_f.id)
            self.assertTupleEqual(received[2].shape, raw_array_ptrs_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_array_ptrs_f,
                received[2],
            )

            # array_ptrs_d
            self.assertEqual(received[3].id, raw_array_ptrs_d.id)
            self.assertTupleEqual(received[3].shape, raw_array_ptrs_d.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_array_ptrs_d,
                received[3],
            )

    @patch_client_popen
    def test_pointer_2d(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("cArrayAndPtr2D", [1, 2])

        ################## cArrayAndPtr2D::1 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show ptr_ptrs_f --dims 2 3")
            self.debugger().execute("dave show ptr_ptrs_d --dims 2 3")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 2, RawEntityList)

            # ptrs_f
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            raw_ptrs_f: RawContainer = received[0].raw_entities[0]
            self.assertContainer2DInvariants(raw_ptrs_f)
            self.assertTupleEqual(raw_ptrs_f.original_shape, (2, 3))
            self.assertEqual(raw_ptrs_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_ptrs_f.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_ptrs_f)

            # ptrs_d
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_ptrs_d: RawContainer = received[1].raw_entities[0]
            self.assertContainer2DInvariants(raw_ptrs_d)
            self.assertTupleEqual(raw_ptrs_d.original_shape, (2, 3))
            self.assertEqual(raw_ptrs_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(raw_ptrs_d.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_ptrs_d)

        ############# cArrayAndPtr2D::2 - (0, 0, 0, 1, -1, 0) ############
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 2, RawContainer.InScopeUpdate)

            # ptrs_f
            self.assertEqual(received[0].id, raw_ptrs_f.id)
            self.assertTupleEqual(received[0].shape, raw_ptrs_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_ptrs_f,
                received[0],
            )

            # ptrs_d
            self.assertEqual(received[1].id, raw_ptrs_d.id)
            self.assertTupleEqual(received[1].shape, raw_ptrs_d.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_ptrs_d,
                received[1],
            )

    @patch_client_popen
    def test_array_2d(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("arrayAndStaticSpan2D", [1, 2])

        ################## arrayAndStaticSpan2D::1 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show array_array_f")
            self.debugger().execute("dave show array_span_f")
            self.debugger().execute("dave show array_vector_d")
            self.debugger().execute("dave show array_dynspan_d")
            # self.debugger().execute("dave show array_nested")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawEntityList)

            # array_array_f
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            raw_array_array_f: RawContainer = received[0].raw_entities[0]
            self.assertContainer2DInvariants(raw_array_array_f)
            self.assertTupleEqual(raw_array_array_f.original_shape, (2, 3))
            self.assertEqual(raw_array_array_f.sample_type, SampleType.FLOAT)
            self.assertEqual(
                raw_array_array_f.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_array_array_f
            )

            # array_span_f
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_array_span_f: RawContainer = received[1].raw_entities[0]
            self.assertContainer2DInvariants(raw_array_span_f)
            self.assertTupleEqual(raw_array_span_f.original_shape, (2, 3))
            self.assertEqual(raw_array_span_f.sample_type, SampleType.FLOAT)
            self.assertEqual(
                raw_array_span_f.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_array_span_f
            )

            # array_vector_d
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawContainer)
            raw_array_vector_d: RawContainer = received[2].raw_entities[0]
            self.assertContainer2DInvariants(raw_array_vector_d)
            self.assertTupleEqual(raw_array_vector_d.original_shape, (2, 3))
            self.assertEqual(raw_array_vector_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(
                raw_array_vector_d.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_array_vector_d
            )

            # array_dynspan_d
            self.assertEqual(len(received[3].raw_entities), 1)
            self.assertIsInstance(received[3].raw_entities[0], RawContainer)
            raw_array_dynspan_d: RawContainer = received[3].raw_entities[0]
            self.assertContainer2DInvariants(raw_array_dynspan_d)
            self.assertTupleEqual(raw_array_dynspan_d.original_shape, (2, 3))
            self.assertEqual(raw_array_dynspan_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(
                raw_array_dynspan_d.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_array_dynspan_d
            )

        ############# arrayAndStaticSpan2D::2 - (0, 0, 0, 1, -1, 0) ############
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # array_array_f
            self.assertEqual(received[0].id, raw_array_array_f.id)
            self.assertTupleEqual(received[0].shape, raw_array_array_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_array_array_f,
                received[0],
            )

            # array_span_f
            self.assertEqual(received[1].id, raw_array_span_f.id)
            self.assertTupleEqual(received[1].shape, raw_array_span_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_array_span_f,
                received[1],
            )

            # array_vector_d
            self.assertEqual(received[2].id, raw_array_vector_d.id)
            self.assertTupleEqual(received[2].shape, raw_array_vector_d.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_array_vector_d,
                received[2],
            )

            # array_dynspan_d
            self.assertEqual(received[3].id, raw_array_dynspan_d.id)
            self.assertTupleEqual(received[3].shape, raw_array_dynspan_d.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_array_dynspan_d,
                received[3],
            )

    @patch_client_popen
    def test_span_static_2d(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("arrayAndStaticSpan2D", [1, 2])

        ################## arrayAndStaticSpan2D::1 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show span_array_f")
            self.debugger().execute("dave show span_span_f")
            self.debugger().execute("dave show span_vector_d")
            self.debugger().execute("dave show span_dynspan_d")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawEntityList)

            # span_array_f
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            raw_span_array_f: RawContainer = received[0].raw_entities[0]
            self.assertContainer2DInvariants(raw_span_array_f)
            self.assertTupleEqual(raw_span_array_f.original_shape, (2, 3))
            self.assertEqual(raw_span_array_f.sample_type, SampleType.FLOAT)
            self.assertEqual(
                raw_span_array_f.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_span_array_f
            )

            # span_span_f
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_span_span_f: RawContainer = received[1].raw_entities[0]
            self.assertContainer2DInvariants(raw_span_span_f)
            self.assertTupleEqual(raw_span_span_f.original_shape, (2, 3))
            self.assertEqual(raw_span_span_f.sample_type, SampleType.FLOAT)
            self.assertEqual(
                raw_span_span_f.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_span_span_f)

            # span_vector_d
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawContainer)
            raw_span_vector_d: RawContainer = received[2].raw_entities[0]
            self.assertContainer2DInvariants(raw_span_vector_d)
            self.assertTupleEqual(raw_span_vector_d.original_shape, (2, 3))
            self.assertEqual(raw_span_vector_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(
                raw_span_vector_d.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_span_vector_d
            )

            # span_dynspan_d
            self.assertEqual(len(received[3].raw_entities), 1)
            self.assertIsInstance(received[3].raw_entities[0], RawContainer)
            raw_span_dynspan_d: RawContainer = received[3].raw_entities[0]
            self.assertContainer2DInvariants(raw_span_dynspan_d)
            self.assertTupleEqual(raw_span_dynspan_d.original_shape, (2, 3))
            self.assertEqual(raw_span_dynspan_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(
                raw_span_dynspan_d.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_span_dynspan_d
            )

        ############# arrayAndStaticSpan2D::2 - (0, 0, 0, 1, -1, 0) ############
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # span_array_f
            self.assertEqual(received[0].id, raw_span_array_f.id)
            self.assertTupleEqual(received[0].shape, raw_span_array_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_span_array_f,
                received[0],
            )

            # span_span_f
            self.assertEqual(received[1].id, raw_span_span_f.id)
            self.assertTupleEqual(received[1].shape, raw_span_span_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_span_span_f,
                received[1],
            )

            # span_vector_d
            self.assertEqual(received[2].id, raw_span_vector_d.id)
            self.assertTupleEqual(received[2].shape, raw_span_vector_d.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_span_vector_d,
                received[2],
            )

            # span_dynspan_d
            self.assertEqual(received[3].id, raw_span_dynspan_d.id)
            self.assertTupleEqual(received[3].shape, raw_span_dynspan_d.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_span_dynspan_d,
                received[3],
            )

    @patch_client_popen
    def test_vector_2d(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("vectorAndDynSpan2D", [1, 2])

        ################## vectorAndDynSpan2D::1 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show vector_array_f")
            self.debugger().execute("dave show vector_span_f")
            self.debugger().execute("dave show vector_vector_d")
            self.debugger().execute("dave show vector_span_d")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawEntityList)

            # vector_array_f
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            raw_vector_array_f: RawContainer = received[0].raw_entities[0]
            self.assertContainer2DInvariants(raw_vector_array_f)
            self.assertTupleEqual(raw_vector_array_f.original_shape, (2, 3))
            self.assertEqual(raw_vector_array_f.sample_type, SampleType.FLOAT)
            self.assertEqual(
                raw_vector_array_f.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_vector_array_f
            )

            # vector_span_f
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_vector_span_f: RawContainer = received[1].raw_entities[0]
            self.assertContainer2DInvariants(raw_vector_span_f)
            self.assertTupleEqual(raw_vector_span_f.original_shape, (2, 3))
            self.assertEqual(raw_vector_span_f.sample_type, SampleType.FLOAT)
            self.assertEqual(
                raw_vector_span_f.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_vector_span_f
            )

            # vector_vector_d
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawContainer)
            raw_vector_vector_d: RawContainer = received[2].raw_entities[0]
            self.assertContainer2DInvariants(raw_vector_vector_d)
            self.assertTupleEqual(raw_vector_vector_d.original_shape, (2, 3))
            self.assertEqual(raw_vector_vector_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(
                raw_vector_vector_d.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_vector_vector_d
            )

            # vector_dynspan_d
            self.assertEqual(len(received[3].raw_entities), 1)
            self.assertIsInstance(received[3].raw_entities[0], RawContainer)
            raw_vector_dynspan_d: RawContainer = received[3].raw_entities[0]
            self.assertContainer2DInvariants(raw_vector_dynspan_d)
            self.assertTupleEqual(raw_vector_dynspan_d.original_shape, (2, 3))
            self.assertEqual(raw_vector_dynspan_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(
                raw_vector_dynspan_d.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_vector_dynspan_d
            )

        ############# vectorAndDynSpan2D::2 - (0, 0, 0, 1, -1, 0) ############
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # vector_array_f
            self.assertEqual(received[0].id, raw_vector_array_f.id)
            self.assertTupleEqual(received[0].shape, raw_vector_array_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_vector_array_f,
                received[0],
            )

            # vector_span_f
            self.assertEqual(received[1].id, raw_vector_span_f.id)
            self.assertTupleEqual(received[1].shape, raw_vector_span_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_vector_span_f,
                received[1],
            )

            # vector_vector_d
            self.assertEqual(received[2].id, raw_vector_vector_d.id)
            self.assertTupleEqual(received[2].shape, raw_vector_vector_d.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_vector_vector_d,
                received[2],
            )

            # vector_dynspan_d
            self.assertEqual(received[3].id, raw_vector_dynspan_d.id)
            self.assertTupleEqual(
                received[3].shape, raw_vector_dynspan_d.original_shape
            )
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_vector_dynspan_d,
                received[3],
            )

    @patch_client_popen
    def test_dyn_span_2d(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("vectorAndDynSpan2D", [1, 2])

        ################## vectorAndDynSpan2D::1 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show span_array_f")
            self.debugger().execute("dave show span_span_f")
            self.debugger().execute("dave show span_vector_d")
            self.debugger().execute("dave show span_span_d")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawEntityList)

            # span_array_f
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            raw_span_array_f: RawContainer = received[0].raw_entities[0]
            self.assertContainer2DInvariants(raw_span_array_f)
            self.assertTupleEqual(raw_span_array_f.original_shape, (2, 3))
            self.assertEqual(raw_span_array_f.sample_type, SampleType.FLOAT)
            self.assertEqual(
                raw_span_array_f.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_span_array_f
            )

            # span_span_f
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_span_span_f: RawContainer = received[1].raw_entities[0]
            self.assertContainer2DInvariants(raw_span_span_f)
            self.assertTupleEqual(raw_span_span_f.original_shape, (2, 3))
            self.assertEqual(raw_span_span_f.sample_type, SampleType.FLOAT)
            self.assertEqual(
                raw_span_span_f.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_span_span_f)

            # span_vector_d
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawContainer)
            raw_span_vector_d: RawContainer = received[2].raw_entities[0]
            self.assertContainer2DInvariants(raw_span_vector_d)
            self.assertTupleEqual(raw_span_vector_d.original_shape, (2, 3))
            self.assertEqual(raw_span_vector_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(
                raw_span_vector_d.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_span_vector_d
            )

            # span_span_d
            self.assertEqual(len(received[3].raw_entities), 1)
            self.assertIsInstance(received[3].raw_entities[0], RawContainer)
            raw_span_span_d: RawContainer = received[3].raw_entities[0]
            self.assertContainer2DInvariants(raw_span_span_d)
            self.assertTupleEqual(raw_span_span_d.original_shape, (2, 3))
            self.assertEqual(raw_span_span_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(
                raw_span_span_d.default_layout, RawContainer.Layout.REAL_2D
            )
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_span_span_d)

        ############# vectorAndDynSpan2D::2 - (0, 0, 0, 1, -1, 0) ############
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # span_array_f
            self.assertEqual(received[0].id, raw_span_array_f.id)
            self.assertTupleEqual(received[0].shape, raw_span_array_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_span_array_f,
                received[0],
            )

            # span_span_f
            self.assertEqual(received[1].id, raw_span_span_f.id)
            self.assertTupleEqual(received[1].shape, raw_span_span_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_span_span_f,
                received[1],
            )

            # span_vector_d
            self.assertEqual(received[2].id, raw_span_vector_d.id)
            self.assertTupleEqual(received[2].shape, raw_span_vector_d.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_span_vector_d,
                received[2],
            )

            # span_span_d
            self.assertEqual(received[3].id, raw_span_span_d.id)
            self.assertTupleEqual(received[3].shape, raw_span_span_d.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0),
                raw_span_span_d,
                received[3],
            )
