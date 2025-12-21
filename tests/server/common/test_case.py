from __future__ import annotations
from pathlib import Path
from typing import Any, List, Tuple, Union
import unittest
import struct
from abc import ABC, abstractmethod
import cmath

from common.debugger import DebuggerAbstraction


class TestCaseBase(unittest.TestCase, ABC):
    """
    A custom TestCase class to use for DAVE server's unit tests

    The caller must provide a BINARY and BINARY_HASH for each subclass implementation

    Both setup() and tearDown() methods are already implemented and will
    automatically cleanup the debugger's state and load the given binary
    """

    TYPE: type[TestCaseBase] = None
    BINARY: Path = None
    BINARY_HASH: str = None

    @staticmethod
    @abstractmethod
    def debugger() -> DebuggerAbstraction:
        pass

    @classmethod
    def declare_as_base_test_class(cls):
        TestCaseBase.TYPE = cls

    def assertIsListOf(self, suspects: List[Any], size: int, cls: type[Any]):
        self.assertEqual(len(suspects), size)
        for suspect in suspects:
            self.assertIsInstance(suspect, cls)

    def assertContainerContent(
        self, expected: Tuple[Any], raw_container, container_update=None
    ):
        if container_update:
            total_samples = container_update.shape[0] * container_update.shape[1]
            array = container_update.data
        else:
            total_samples = (
                raw_container.original_shape[0] * raw_container.original_shape[1]
            )
            array = raw_container.data
        fmt = "".join(
            raw_container.sample_type.struct_fmt() for _ in range(total_samples)
        )
        samples = struct.unpack(fmt, array)
        if raw_container.sample_type.is_complex():
            samples = tuple(
                complex(samples[n], samples[n + 1]) for n in range(0, len(samples), 2)
            )

        self.assertTupleEqual(expected, samples)

    def assertTupleEqual(self, tuple1: Tuple[Any], tuple2: Tuple[Any]):
        tuple1 = tuple("NaN" if cmath.isnan(val) else val for val in tuple1)
        tuple2 = tuple("NaN" if cmath.isnan(val) else val for val in tuple2)
        super().assertTupleEqual(tuple1, tuple2)
