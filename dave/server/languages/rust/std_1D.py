import re
import sys
from typing import List, Tuple

from dave.common.logger import Logger
from dave.server.language_type import LanguageType

from ...container import SampleType, Container1D
from ...debuggers.value import AbstractValue, DebuggerMemoryError
from .std_base import RustSlice, RustVector


class RustArray1D(Container1D):
    # LLDB type syntac: type[size]
    # GBD type syntax: [type; size]
    __REGEX = rf"^\[{SampleType.regex()}; (\d+)\]|{SampleType.regex()}\[(\d+)\]$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        typename = dbg_value.typename()
        sample_type, self.__size = self.parse_typename(typename)
        super().__init__(dbg_value, name, sample_type)

    @property
    def size(self) -> int:
        return self.__size

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @classmethod
    def parse_typename(cls, typename: str) -> Tuple[SampleType, int]:
        err = TypeError(
            f"RustArray1D could not parse {typename} as a valid rust array type"
        )

        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise err

        try:
            sample_type = SampleType.parse(re_match.group(1) or re_match.group(3))
        except ValueError:
            raise err
        size = int(re_match.group(2) or re_match.group(4))

        return (sample_type, size)

    def read_from_debugger(self) -> bytearray:
        assert isinstance(self._value, AbstractValue)
        return self._value.readmemory(self._value.address(), self.byte_size)

    @staticmethod
    def formatter_compatible():
        return False


class RustSlice1D(Container1D):
    __REGEX = rf"^&\s?(?:mut\s?)?\[{SampleType.regex()}]$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        typename = dbg_value.typename()
        sample_type = self.parse_typename(typename)[0]
        self.__slice = RustSlice(dbg_value)
        super().__init__(dbg_value, name, sample_type)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @classmethod
    def parse_typename(cls, typename: str) -> Tuple[SampleType, int]:
        err = TypeError(
            f"RustSlice1D could not parse {typename} as a valid rust array type"
        )

        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise err

        try:
            sample_type = SampleType.parse(re_match.group(1))
        except ValueError:
            raise err

        return (sample_type, None)

    @property
    def size(self) -> int:
        return self.__slice.size

    def __data_ptr(self) -> int:
        return int(self.__slice.data_ptr_value())

    def read_from_debugger(self) -> bytearray:
        assert isinstance(self._value, AbstractValue)
        if self.size <= 0:
            raise DebuggerMemoryError("slice dimension is <= 0")
        return self._value.readmemory(self.__data_ptr(), self.byte_size)

    @staticmethod
    def formatter_compatible():
        return False


class RustVector1D(Container1D):
    __REGEX = rf"^(?:mut\s)?alloc::vec::Vec<{SampleType.regex()},.*>$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        typename = dbg_value.typename()
        sample_type = self.parse_typename(typename)[0]
        self.__vector = RustVector(dbg_value)
        super().__init__(dbg_value, name, sample_type)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @classmethod
    def parse_typename(cls, typename: str) -> Tuple[SampleType, int]:
        err = TypeError(
            f"RustVector1D could not parse {typename} as a valid rust array type"
        )

        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise err

        try:
            sample_type = SampleType.parse(re_match.group(1))
        except ValueError:
            raise err

        return (sample_type, None)

    @property
    def size(self) -> int:
        return self.__vector.size

    def __data_ptr(self) -> int:
        return int(self.__vector.data_ptr_value())

    def read_from_debugger(self) -> bytearray:
        assert isinstance(self._value, AbstractValue)
        if self.size <= 0:
            raise DebuggerMemoryError("vector dimension is <= 0")
        return self._value.readmemory(self.__data_ptr(), self.byte_size)

    @staticmethod
    def formatter_compatible():
        return False


RustArray1D.register(LanguageType.RUST)
RustSlice1D.register(LanguageType.RUST)
RustVector1D.register(LanguageType.RUST)
