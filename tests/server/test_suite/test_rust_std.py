from common import TestCaseBase, RUST_BUILD_DIR
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

class TestRustStd(TestCaseBase.TYPE):
    BINARY = RUST_BUILD_DIR / "std_tests"

    def assertContainer1DInvariants(self, array: RawContainer):
        self.assertListEqual(array.possible_layout, CONTAINER_1D_LAYOUTS)
        self.assertEqual(array.dimensions_fixed, False)
        self.assertEqual(array.interleaved, False)

    def assertContainer2DInvariants(self, array: RawContainer):
        self.assertListEqual(array.possible_layout, CONTAINER_2D_LAYOUTS)
        self.assertEqual(array.dimensions_fixed, True)
        self.assertEqual(array.interleaved, False)

    @patch_client_popen
    def test_vector(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("std_tests::vector_and_slice", [1, 2])

        ################## vector_and_slice::1 - All zeros ##################
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

        ################## vector_and_slice::2 - (1, -1, 0) ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # vector_f
            self.assertEqual(received[0].id, raw_vector_f.id)
            self.assertTupleEqual(received[0].shape, raw_vector_f.original_shape)
            self.assertContainerContent(
                (1.0, -1.0, 0.0), raw_vector_f, received[0]
            )

            # vector_c
            self.assertEqual(received[1].id, raw_vector_c.id)
            self.assertTupleEqual(received[1].shape, raw_vector_c.original_shape)
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0 + 0j), raw_vector_c, received[1]
            )

            # vector_d
            self.assertEqual(received[2].id, raw_vector_d.id)
            self.assertTupleEqual(received[2].shape, raw_vector_d.original_shape)
            self.assertContainerContent(
                (1.0, -1.0, 0.0), raw_vector_d, received[2]
            )

            # vector_cd
            self.assertEqual(received[3].id, raw_vector_cd.id)
            self.assertTupleEqual(received[3].shape, raw_vector_cd.original_shape)
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0 + 0j), raw_vector_cd, received[3]
            )

    @patch_client_popen
    def test_array(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("std_tests::array", [1, 2])

        ################## array::1 - All zeros ##################
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
            self.assertContainerContent(
                (0.0 + 0j, 0.0 + 0j, 0.0 + 0j), raw_array_c
            )

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
            self.assertContainerContent(
                (0.0 + 0j, 0.0 + 0j, 0.0 + 0j), raw_array_cd
            )
        
        ################## array::2 - (1, -1, 0) ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # array_f
            self.assertEqual(received[0].id, raw_array_f.id)
            self.assertTupleEqual(received[0].shape, raw_array_f.original_shape)
            self.assertContainerContent(
                (1.0, -1.0, 0.0), raw_array_f, received[0]
            )

            # array_c
            self.assertEqual(received[1].id, raw_array_c.id)
            self.assertTupleEqual(received[1].shape, raw_array_c.original_shape)
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0 + 0j), raw_array_c, received[1]
            )

            # array_d
            self.assertEqual(received[2].id, raw_array_d.id)
            self.assertTupleEqual(received[2].shape, raw_array_d.original_shape)
            self.assertContainerContent(
                (1.0, -1.0, 0.0), raw_array_d, received[2]
            )

            # array_cd
            self.assertEqual(received[3].id, raw_array_cd.id)
            self.assertTupleEqual(received[3].shape, raw_array_cd.original_shape)
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0 + 0j), raw_array_cd, received[3]
            )

    @patch_client_popen
    def test_slice(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("std_tests::vector_and_slice", [1, 2])

        ################## vector_and_slice::1 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show _slice_f")
            self.debugger().execute("dave show _slice_c")
            self.debugger().execute("dave show _slice_d")
            self.debugger().execute("dave show _slice_cd")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawEntityList)

            # slice_f
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            raw_slice_f: RawContainer = received[0].raw_entities[0]
            self.assertContainer1DInvariants(raw_slice_f)
            self.assertTupleEqual(raw_slice_f.original_shape, (1, 3))
            self.assertEqual(raw_slice_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_slice_f.default_layout, RawContainer.Layout.REAL_1D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_slice_f)

            # slice_c
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_slice_c: RawContainer = received[1].raw_entities[0]
            self.assertContainer1DInvariants(raw_slice_c)
            self.assertTupleEqual(raw_slice_c.original_shape, (1, 3))
            self.assertEqual(raw_slice_c.sample_type, SampleType.CPX_F)
            self.assertEqual(raw_slice_c.default_layout, RawContainer.Layout.CPX_1D)
            self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_slice_c)

            # slice_d
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawContainer)
            raw_slice_d: RawContainer = received[2].raw_entities[0]
            self.assertContainer1DInvariants(raw_slice_d)
            self.assertTupleEqual(raw_slice_d.original_shape, (1, 3))
            self.assertEqual(raw_slice_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(raw_slice_d.default_layout, RawContainer.Layout.REAL_1D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_slice_d)

            # slice_cd
            self.assertEqual(len(received[3].raw_entities), 1)
            self.assertIsInstance(received[3].raw_entities[0], RawContainer)
            raw_slice_cd: RawContainer = received[3].raw_entities[0]
            self.assertContainer1DInvariants(raw_slice_cd)
            self.assertTupleEqual(raw_slice_cd.original_shape, (1, 3))
            self.assertEqual(raw_slice_cd.sample_type, SampleType.CPX_D)
            self.assertEqual(raw_slice_cd.default_layout, RawContainer.Layout.CPX_1D)
            self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_slice_cd)

        ################## vector_and_slice::2 - (1, -1, 0) ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # slice_f
            self.assertEqual(received[0].id, raw_slice_f.id)
            self.assertTupleEqual(received[0].shape, raw_slice_f.original_shape)
            self.assertContainerContent(
                (1.0, -1.0, 0.0), raw_slice_f, received[0]
            )

            # slice_c
            self.assertEqual(received[1].id, raw_slice_c.id)
            self.assertTupleEqual(received[1].shape, raw_slice_c.original_shape)
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0 + 0j), raw_slice_c, received[1]
            )

            # slice_d
            self.assertEqual(received[2].id, raw_slice_d.id)
            self.assertTupleEqual(received[2].shape, raw_slice_d.original_shape)
            self.assertContainerContent(
                (1.0, -1.0, 0.0), raw_slice_d, received[2]
            )

            # slice_cd
            self.assertEqual(received[3].id, raw_slice_cd.id)
            self.assertTupleEqual(received[3].shape, raw_slice_cd.original_shape)
            self.assertContainerContent(
                (1 + 1j, -1 - 1j, 0 + 0j), raw_slice_cd, received[3]
            )

    @patch_client_popen
    def test_array_2d(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("std_tests::array_2d", [1, 2])

        ################## array_2d::1 - All zeros ##################
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show array_array_f")
            self.debugger().execute("dave show _array_slice_f")
            self.debugger().execute("dave show array_vector_d")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 3, RawEntityList)

            # array_array_f
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            raw_array_array_f: RawContainer = received[0].raw_entities[0]
            self.assertContainer2DInvariants(raw_array_array_f)
            self.assertTupleEqual(raw_array_array_f.original_shape, (2, 3))
            self.assertEqual(raw_array_array_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_array_array_f.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_array_array_f)

            # _array_slice_f
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_array_slice_f: RawContainer = received[1].raw_entities[0]
            self.assertContainer2DInvariants(raw_array_slice_f)
            self.assertTupleEqual(raw_array_slice_f.original_shape, (2, 3))
            self.assertEqual(raw_array_slice_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_array_slice_f.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_array_slice_f)

            # array_vector_d
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawContainer)
            raw_array_vector_d: RawContainer = received[2].raw_entities[0]
            self.assertContainer2DInvariants(raw_array_vector_d)
            self.assertTupleEqual(raw_array_vector_d.original_shape, (2, 3))
            self.assertEqual(raw_array_vector_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(raw_array_vector_d.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_array_vector_d)

        ################## array_2d::2 - ((0, 0, 0), (1, -1, 0)) ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 3, RawContainer.InScopeUpdate)

            # array_array_f
            self.assertEqual(received[0].id, raw_array_array_f.id)
            self.assertTupleEqual(received[0].shape, raw_array_array_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0), raw_array_array_f, received[0]
            )

            # _array_slice_f
            self.assertEqual(received[1].id, raw_array_slice_f.id)
            self.assertTupleEqual(received[1].shape, raw_array_slice_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0), raw_array_slice_f, received[1]
            )

            # array_vector_d
            self.assertEqual(received[2].id, raw_array_vector_d.id)
            self.assertTupleEqual(received[2].shape, raw_array_vector_d.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0), raw_array_vector_d, received[2]
            )

    @patch_client_popen
    def test_vector_2d(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("std_tests::vector_and_slice_2d", [1, 2])

        ############ vector_and_slice_2d::1 - All zeros ############
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show vector_array_f")
            self.debugger().execute("dave show _vector_slice_f")
            self.debugger().execute("dave show vector_vector_d")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 3, RawEntityList)

            # vector_array_f
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            raw_vector_array_f: RawContainer = received[0].raw_entities[0]
            self.assertContainer2DInvariants(raw_vector_array_f)
            self.assertTupleEqual(raw_vector_array_f.original_shape, (2, 3))
            self.assertEqual(raw_vector_array_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_vector_array_f.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_vector_array_f)

            # _vector_slice_f
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_vector_slice_f: RawContainer = received[1].raw_entities[0]
            self.assertContainer2DInvariants(raw_vector_slice_f)
            self.assertTupleEqual(raw_vector_slice_f.original_shape, (2, 3))
            self.assertEqual(raw_vector_slice_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_vector_slice_f.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_vector_slice_f)

            # vector_vector_d
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawContainer)
            raw_vector_vector_d: RawContainer = received[2].raw_entities[0]
            self.assertContainer2DInvariants(raw_vector_vector_d)
            self.assertTupleEqual(raw_vector_vector_d.original_shape, (2, 3))
            self.assertEqual(raw_vector_vector_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(raw_vector_vector_d.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_vector_vector_d)

        ############ vector_and_slice_2d::2 - ((0, 0, 0), (1, -1, 0)) ############
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 3, RawContainer.InScopeUpdate)

            # vector_array_f
            self.assertEqual(received[0].id, raw_vector_array_f.id)
            self.assertTupleEqual(received[0].shape, raw_vector_array_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0), raw_vector_array_f, received[0]
            )

            # _vector_slice_f
            self.assertEqual(received[1].id, raw_vector_slice_f.id)
            self.assertTupleEqual(received[1].shape, raw_vector_slice_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0), raw_vector_slice_f, received[1]
            )

            # vector_vector_d
            self.assertEqual(received[2].id, raw_vector_vector_d.id)
            self.assertTupleEqual(received[2].shape, raw_vector_vector_d.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0), raw_vector_vector_d, received[2]
            )

    @patch_client_popen
    def test_slice_2d(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("std_tests::vector_and_slice_2d", [1, 2])

        ############ vector_and_slice_2d::1 - All zeros ############
        self.debugger().run()
        with self.failFastSubTestAtLocation():
            self.debugger().execute("dave show _slice_array_f")
            self.debugger().execute("dave show _slice_slice_f")
            self.debugger().execute("dave show _slice_vector_d")

            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 3, RawEntityList)

            # _slice_array_f
            self.assertEqual(len(received[0].raw_entities), 1)
            self.assertIsInstance(received[0].raw_entities[0], RawContainer)
            raw_slice_array_f: RawContainer = received[0].raw_entities[0]
            self.assertContainer2DInvariants(raw_slice_array_f)
            self.assertTupleEqual(raw_slice_array_f.original_shape, (2, 3))
            self.assertEqual(raw_slice_array_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_slice_array_f.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_slice_array_f)

            # _slice_slice_f
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_slice_slice_f: RawContainer = received[1].raw_entities[0]
            self.assertContainer2DInvariants(raw_slice_slice_f)
            self.assertTupleEqual(raw_slice_slice_f.original_shape, (2, 3))
            self.assertEqual(raw_slice_slice_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_slice_slice_f.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_slice_slice_f)

            # _slice_vector_d
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawContainer)
            raw_slice_vector_d: RawContainer = received[2].raw_entities[0]
            self.assertContainer2DInvariants(raw_slice_vector_d)
            self.assertTupleEqual(raw_slice_vector_d.original_shape, (2, 3))
            self.assertEqual(raw_slice_vector_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(raw_slice_vector_d.default_layout, RawContainer.Layout.REAL_2D)
            self.assertContainerContent((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), raw_slice_vector_d)

        ############ vector_and_slice_2d::2 - ((0, 0, 0), (1, -1, 0)) ############
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 3, RawContainer.InScopeUpdate)

            # _slice_array_f
            self.assertEqual(received[0].id, raw_slice_array_f.id)
            self.assertTupleEqual(received[0].shape, raw_slice_array_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0), raw_slice_array_f, received[0]
            )

            # _slice_slice_f
            self.assertEqual(received[1].id, raw_slice_slice_f.id)
            self.assertTupleEqual(received[1].shape, raw_slice_slice_f.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0), raw_slice_slice_f, received[1]
            )

            # _slice_vector_d
            self.assertEqual(received[2].id, raw_slice_vector_d.id)
            self.assertTupleEqual(received[2].shape, raw_slice_vector_d.original_shape)
            self.assertContainerContent(
                (0.0, 0.0, 0.0, 1.0, -1.0, 0.0), raw_slice_vector_d, received[2]
            )