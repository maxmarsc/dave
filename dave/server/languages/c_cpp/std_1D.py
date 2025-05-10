# from abc import ABC, abstractmethod
# from enum import Enum
import re
from typing import List, Tuple

from dave.common.logger import Logger

# import gdb  # type: ignore
# import gdb.types  # type: ignore


from ...container import SampleType, Container1D
from ...debuggers.value import AbstractValue, DebuggerMemoryError
from .std_base import StdVector, StdSpan


class CArray1D(Container1D):
    __REGEX = rf"^(?:const\s+)?{SampleType.regex()}\s*\[(\d+)\]$"

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
        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"CArray1D could not parse {typename} as a valid C array type"
            )

        return (SampleType.parse(re_match.group(1)), int(re_match.group(2)))

    def read_from_debugger(self) -> bytearray:
        assert isinstance(self._value, AbstractValue)
        return self._value.readmemory(self._value.address(), self.byte_size)

    @staticmethod
    def formatter_compatible():
        return False


class Pointer1D(Container1D):
    __REGEX = rf"^(?:const\s+)?{SampleType.regex()}\s*\*$"

    def __init__(self, dbg_value: AbstractValue, name: str, dims: List[int]):
        if len(dims) != 1:
            raise TypeError("Pointer container requires exactly one dimension")
        typename = dbg_value.typename()
        sample_type = self.parse_typename(typename)[0]
        self.__size = dims[0]
        super().__init__(dbg_value, name, sample_type)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @classmethod
    def parse_typename(cls, typename: str) -> Tuple[SampleType, None]:
        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"Pointer1D could not parse {typename} as a valid C array type"
            )

        return (SampleType.parse(re_match.group(1)), None)

    @property
    def size(self) -> int:
        return self.__size

    def read_from_debugger(self) -> bytearray:
        assert isinstance(self._value, AbstractValue)
        return self._value.readmemory(int(self._value), self.byte_size)

    @staticmethod
    def formatter_compatible():
        return False


class StdArray1D(Container1D):
    __REGEX = rf"^(?:const\s+)?std::(?:\_\_1\:\:)?array<{SampleType.regex()},\s*(\d+)[a-z]*>\s*$"

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
        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"StdArray1D could not parse {typename} as a valid std::array type"
            )

        return (SampleType.parse(re_match.group(1)), int(re_match.group(2)))

    def read_from_debugger(self) -> bytearray:
        assert isinstance(self._value, AbstractValue)
        return self._value.readmemory(self._value.address(), self.byte_size)

    @staticmethod
    def formatter_compatible():
        return False


class StdVector1D(Container1D):
    __REGEX = rf"^(?:const\s+)?std::(?:\_\_1\:\:)?vector<{SampleType.regex()},.*>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        self.__vec = StdVector(dbg_value)
        typename = dbg_value.typename()
        sample_type = self.parse_typename(typename)[0]
        super().__init__(dbg_value, name, sample_type)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @classmethod
    def parse_typename(cls, typename: str) -> Tuple[SampleType, int]:
        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"StdVector1D could not parse {typename} as a valid std::vector type"
            )
        return (SampleType.parse(re_match.group(1)), None)

    @property
    def size(self) -> int:
        return self.__vec.size

    def __data_ptr_value(self) -> AbstractValue:
        return self.__vec.data_ptr_value()

    def read_from_debugger(self) -> bytearray:
        assert isinstance(self._value, AbstractValue)
        if self.size <= 0:
            raise DebuggerMemoryError("std::vector dimension is <= 0")
        return self._value.readmemory(int(self.__data_ptr_value()), self.byte_size)

    @staticmethod
    def formatter_compatible():
        return False


class StdSpan1D(Container1D):
    __REGEX = rf"^(?:const\s+)?(?:std|gsl)::(?:\_\_1\:\:)?span<(?:const)?\s*{SampleType.regex()}\s*(?:const)?,\s*(\d+)[a-z]*>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        typename = dbg_value.typename()
        sample_type, size = self.parse_typename(typename)
        self.__span = StdSpan(dbg_value, size)
        super().__init__(dbg_value, name, sample_type)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @classmethod
    def parse_typename(cls, typename: str) -> Tuple[SampleType, int]:
        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"StdSpan1D could not parse {typename} as a valid std::span type"
            )

        return (SampleType.parse(re_match.group(1)), int(re_match.group(2)))

    @property
    def size(self) -> int:
        return self.__span.size

    def __data_ptr(self) -> int:
        return int(self.__span.data_ptr_value())

    def read_from_debugger(self) -> bytearray:
        assert isinstance(self._value, AbstractValue)
        if self.size <= 0:
            raise DebuggerMemoryError("std::span dimension is <= 0")
        return self._value.readmemory(self.__data_ptr(), self.byte_size)

    @staticmethod
    def formatter_compatible():
        return False


CArray1D.register()
StdArray1D.register()
StdVector1D.register()
StdSpan1D.register()
Pointer1D.register()
