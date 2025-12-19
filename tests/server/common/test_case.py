from __future__ import annotations
from pathlib import Path
import unittest
from abc import ABC, abstractmethod

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
        # TEST_CASE_BASE = cls

    # @staticmethod
    # def type() -> type[TestCaseBase]:
    #     return TestCaseBase.TYPE
    # global TEST_CASE_BASE
    # return TEST_CASE_BASE


# TEST_CASE_BASE: type[TestCaseBase] = None
