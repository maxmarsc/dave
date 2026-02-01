from __future__ import annotations
import contextlib
from pathlib import Path
from typing import Any, List, Tuple, Union
import unittest
from unittest.case import _OrderedChainMap, _SubTest, _ShouldStop, _subtest_msg_sentinel
import struct
from abc import ABC, abstractmethod
import cmath
import re

from common.debugger import CommandError, DebuggerAbstraction


__unittest = True  # Make sure custom test functions does not show up in the stack trace


def is_numeric(val: object) -> bool:
    return isinstance(val, int) or isinstance(val, float) or isinstance(val, complex)


class TestCaseBase(unittest.TestCase, ABC):
    """
    A custom TestCase class to use for DAVE server's unit tests

    The caller must provide a BINARY path attribute for each subclass implementation

    Both setup() and tearDown() methods are already implemented and will
    automatically cleanup the debugger's state and load the given binary
    """

    TYPE: type[TestCaseBase] = None
    BINARY: Path = None

    @staticmethod
    @abstractmethod
    def debugger() -> DebuggerAbstraction:
        pass

    def _check_for_binary(self):
        if not self.BINARY:
            self.fail("Missing BINARY class attribute")

        # Check the binary file exists
        self.assertTrue(self.BINARY.is_file(), f"Binary {self.BINARY} does not exist")

    @classmethod
    def declare_as_base_test_class(cls):
        TestCaseBase.TYPE = cls

    @contextlib.contextmanager
    def failFastSubTestAtLocation(self, msg=_subtest_msg_sentinel, **params):
        """
        A custom re-implementation of Subtest which always failfast and set the
        current file line in the context message
        """
        params["line"] = self.debugger().get_current_line()
        if self._outcome is None or not self._outcome.result_supports_subtests:
            yield
            return
        parent = self._subtest
        if parent is None:
            params_map = _OrderedChainMap(params)
        else:
            params_map = parent.params.new_child(params)
        self._subtest = _SubTest(self, msg, params_map)
        try:
            with self._outcome.testPartExecutor(self._subtest, subTest=True):
                yield
            if not self._outcome.success:
                result = self._outcome.result
                if result is not None:
                    raise _ShouldStop
            elif self._outcome.expectedFailure:
                # If the test is expecting a failure, we really want to
                # stop now and register the expected failure.
                raise _ShouldStop
        finally:
            self._subtest = parent

    def assertIsListOf(self, suspects: List[Any], size: int, cls: type[Any]):
        self.assertEqual(len(suspects), size)
        for suspect in suspects:
            self.assertIsInstance(suspect, cls)

    def assertExceptionEquals(self, e1: Exception, e2: Exception):
        self.assertIsInstance(e1, Exception)
        self.assertIsInstance(e2, Exception)
        self.assertEqual(type(e1), type(e2))
        self.assertTupleEqual(e1.args, e2.args)

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
        tuple1 = tuple(
            "NaN" if is_numeric(val) and cmath.isnan(val) else val for val in tuple1
        )
        tuple2 = tuple(
            "NaN" if is_numeric(val) and cmath.isnan(val) else val for val in tuple2
        )
        super().assertTupleEqual(tuple1, tuple2)

    def assertPrettyPrinterEqual(
        self, variable_name: str, summary: str, children: List[Tuple[str, str]]
    ):
        obtained_summary, obtained_children = self.debugger().get_variable_printer(
            variable_name
        )
        self.assertEqual(summary, obtained_summary)
        self.assertListEqual(children, obtained_children)

    def assertStartsWith(self, to_check: str, prefix: str):
        try:
            self.assertTrue(to_check.startswith(prefix))
            success = True
        except AssertionError:
            success = False

        if not success:
            prefix_len = len(prefix)
            to_check_fmt_size = prefix_len + 10
            if len(to_check) > to_check_fmt_size:
                to_check_fmt = to_check[: prefix_len + 7] + "..."
            else:
                to_check_fmt = to_check
            raise AssertionError(
                f"\n\t{to_check_fmt[:]}\n does not starts with \n\t{prefix}"
            )

    def assertMatchsRegex(self, to_check: str, pattern: str) -> re.Match:
        ret = re.match(pattern, to_check, re.MULTILINE)
        try:
            self.assertIsNotNone(ret)
            success = True
        except AssertionError:
            success = False

        if not success:
            pattern_len = len(pattern)
            to_check_fmt_size = pattern_len + 10
            if len(to_check) > to_check_fmt_size:
                to_check_fmt = to_check[: pattern_len + 7] + "..."
            else:
                to_check_fmt = to_check
            raise AssertionError(
                f"The regex:\n\t{to_check_fmt[:]}\n does not match with:\n\t{pattern}"
            )
        return ret

    def assertIsCommandErrorWith(self, error: Exception, text: str):
        self.assertIsInstance(error, CommandError)
        self.assertIsInstance(error.args[0], str)
        error_msg: str = error.args[0]
        self.assertTrue(text in error_msg)

    def assertIsIn(self, instance: Any, collection):
        self.assertTrue(instance in collection)
