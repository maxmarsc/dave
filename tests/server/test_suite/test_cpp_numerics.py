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
PINF = float("inf")
NINF = -float("inf")


class TestCppNumerics(TestCaseBase.TYPE):
    BINARY = C_CPP_BUILD_DIR / "std_tests"

    @patch_client_popen
    def test_nan_infs(self, _):
        # Set the breakpoints
        self.debugger().set_breakpoints_at_tags("numericValues", [1, 2])

        ################## numericValues::1 - All zeros ##################
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
            self.assertTupleEqual(raw_array_f.original_shape, (1, 3))
            self.assertEqual(raw_array_f.sample_type, SampleType.FLOAT)
            self.assertEqual(raw_array_f.default_layout, RawContainer.Layout.REAL_1D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_array_f)

            # array_c
            self.assertEqual(len(received[1].raw_entities), 1)
            self.assertIsInstance(received[1].raw_entities[0], RawContainer)
            raw_array_c: RawContainer = received[1].raw_entities[0]
            self.assertTupleEqual(raw_array_c.original_shape, (1, 3))
            self.assertEqual(raw_array_c.sample_type, SampleType.CPX_F)
            self.assertEqual(raw_array_c.default_layout, RawContainer.Layout.CPX_1D)
            self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_array_c)

            # array_d
            self.assertEqual(len(received[2].raw_entities), 1)
            self.assertIsInstance(received[2].raw_entities[0], RawContainer)
            raw_array_d: RawContainer = received[2].raw_entities[0]
            self.assertTupleEqual(raw_array_d.original_shape, (1, 3))
            self.assertEqual(raw_array_d.sample_type, SampleType.DOUBLE)
            self.assertEqual(raw_array_d.default_layout, RawContainer.Layout.REAL_1D)
            self.assertContainerContent((0.0, 0.0, 0.0), raw_array_d)

            # array_cd
            self.assertEqual(len(received[3].raw_entities), 1)
            self.assertIsInstance(received[3].raw_entities[0], RawContainer)
            raw_array_cd: RawContainer = received[3].raw_entities[0]
            self.assertTupleEqual(raw_array_cd.original_shape, (1, 3))
            self.assertEqual(raw_array_cd.sample_type, SampleType.CPX_D)
            self.assertEqual(raw_array_cd.default_layout, RawContainer.Layout.CPX_1D)
            self.assertContainerContent((0 + 0j, 0 + 0j, 0 + 0j), raw_array_cd)

        ################## numericValues::2 - (NaN, +inf, -inf) ##################
        self.debugger().continue_()
        with self.failFastSubTestAtLocation():
            received = MockClient().receive_from_server()
            self.assertIsListOf(received, 4, RawContainer.InScopeUpdate)

            # array_f
            self.assertEqual(received[0].id, raw_array_f.id)
            self.assertTupleEqual(received[0].shape, raw_array_f.original_shape)
            self.assertContainerContent((NAN, PINF, NINF), raw_array_f, received[0])

            # array_c
            self.assertEqual(received[1].id, raw_array_c.id)
            self.assertTupleEqual(received[1].shape, raw_array_c.original_shape)
            self.assertContainerContent((NAN, PINF, NINF), raw_array_c, received[1])

            # array_f
            self.assertEqual(received[2].id, raw_array_d.id)
            self.assertTupleEqual(received[2].shape, raw_array_d.original_shape)
            self.assertContainerContent((NAN, PINF, NINF), raw_array_d, received[2])

            # array_c
            self.assertEqual(received[3].id, raw_array_cd.id)
            self.assertTupleEqual(received[3].shape, raw_array_cd.original_shape)
            self.assertContainerContent((NAN, PINF, NINF), raw_array_cd, received[3])
