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


def byte_array_to_samples(
    array: bytearray, sp: SampleType, shape: Tuple[int, int]
) -> Tuple:
    total = shape[0] * shape[1]
    fmt = "".join(sp.struct_fmt() for _ in range(total))
    samples = struct.unpack(fmt, array)
    if sp.is_complex():
        samples = tuple(
            complex(samples[n], samples[n + 1]) for n in range(0, len(samples), 2)
        )
    return samples


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
        samples_array_f = byte_array_to_samples(
            raw_array_f.data, raw_array_f.sample_type, raw_array_f.original_shape
        )
        self.assertTupleEqual(samples_array_f, (0.0, 0.0, 0.0))

        # array_c
        self.assertEqual(len(received[1].raw_entities), 1)
        self.assertIsInstance(received[1].raw_entities[0], RawContainer)
        raw_array_c: RawContainer = received[1].raw_entities[0]
        self.assertArrayInvariants(raw_array_c)
        self.assertTupleEqual(raw_array_c.original_shape, (1, 3))
        self.assertEqual(raw_array_c.sample_type, SampleType.CPX_F)
        self.assertEqual(raw_array_c.default_layout, RawContainer.Layout.CPX_1D)
        samples_array_c = byte_array_to_samples(
            raw_array_c.data, raw_array_c.sample_type, raw_array_c.original_shape
        )
        self.assertTupleEqual(samples_array_c, (0 + 0j, 0 + 0j, 0 + 0j))

        ################## std_tests.cpp:34 - (1, 0, 0) ##################
        self.debugger().con()
        received = MockClient().receive_from_server()
        self.assertIsListOf(received, 2, RawContainer.InScopeUpdate)

        # array_f
        self.assertEqual(received[0].id, raw_array_f.id)
        self.assertTupleEqual(received[0].shape, raw_array_f.original_shape)
        samples_array_f = byte_array_to_samples(
            received[0].data, raw_array_f.sample_type, received[0].shape
        )
        self.assertTupleEqual(samples_array_f, (1.0, 0.0, 0.0))

        # array_c
        self.assertEqual(received[1].id, raw_array_c.id)
        self.assertTupleEqual(received[1].shape, raw_array_c.original_shape)
        samples_array_c = byte_array_to_samples(
            received[1].data, raw_array_c.sample_type, received[1].shape
        )
        self.assertTupleEqual(samples_array_c, (1 + 1j, 0 + 0j, 0 + 0j))
