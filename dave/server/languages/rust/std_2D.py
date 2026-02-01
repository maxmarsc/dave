from __future__ import annotations

import re
from typing import Callable, List, Optional, Tuple
from pathlib import Path

from dave.common.logger import Logger
from dave.server.language_type import LanguageType

from ...container import Container, Container1D, SampleType, Container2D
from ...entity_factory import EntityFactory
from ...debuggers.value import AbstractValue, DebuggerMemoryError

from .std_base import RustSlice, RustVector
from ..c_cpp.template_parser import parse_template


class RustArrayArray2D(Container2D):
    # LLDB type syntac: type[outer_size][inner_size]
    # GBD type syntax: [[type; inner_size]; outer_size]
    __REGEX = rf"^\[\[{SampleType.regex()}; (\d+)\]; (\d+)\]|{SampleType.regex()}\[(\d+)\]\[(\d+)\]$"

    def __init__(self, dbg_value: AbstractValue, name: str, dims=[]):
        typename = dbg_value.typename()
        sample_type, dim_0, dim_1 = self._parse_typename(typename)
        self.__shape = (dim_0, dim_1)
        super().__init__(dbg_value, name, sample_type)

    def shape(self) -> Tuple[int, int]:
        return self.__shape

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @classmethod
    def _parse_typename(cls, typename: str, **_) -> Tuple[SampleType, int, int]:
        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"RustArrayArray2D could not parse {typename} as a valid 2D rust array type"
            )

        return (
            SampleType.parse(re_match.group(1) or re_match.group(4)),
            int(re_match.group(3) or re_match.group(5)),
            int(re_match.group(2) or re_match.group(6)),
        )

    @property
    def byte_size(self) -> int:
        return self.sample_type.byte_size() * self.shape()[0] * self.shape()[1]

    def read_from_debugger(self) -> bytearray:
        assert isinstance(self._value, AbstractValue)
        return self._value.readmemory(self._value.address(), self.byte_size)

    @staticmethod
    def formatter_compatible():
        return False


class RustArrayAny2D(Container2D):
    # LLDB type syntac: type[size]
    # GBD type syntax: [type; size]
    __REGEX = rf"^\[(.*); (\d+)\]|(.*)\[(\d+)\]$"

    def __init__(self, dbg_value: AbstractValue, name: str, dims=[]):
        typename = dbg_value.typename()
        sample_type, self.__size, _ = self._parse_typename(typename)
        self.__nested_dim = dims
        super().__init__(dbg_value, name, sample_type)

        # Try to build the nested containers
        assert self.__nested_containers is not None

    @property
    def __nested_containers(self) -> List[Container1D]:
        return self._nested_containers(self._value, self.__size, self.__nested_dim)

    def shape(self) -> Tuple[int, int]:
        return (
            self.__size,
            self.__nested_containers[0].size,
        )

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @classmethod
    def _parse_typename(
        cls, typename: str, **_
    ) -> Tuple[SampleType, int, Optional[int]]:
        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"RustArrayAny2D could not parse {typename} as a valid Rust array type"
            )

        # Check if contains a nested valid 1D container
        nested_typename = re_match.group(1) or re_match.group(3)
        nested = EntityFactory().check_valid_simple(nested_typename)
        if nested is None or not issubclass(nested, Container1D):
            raise TypeError(
                f"RustArrayAny2D could not parse nested type {nested_typename} as a valid Container1D type"
            )

        sample_type, nested_size = nested.parse_typename(nested_typename)

        return (sample_type, int(re_match.group(2) or re_match.group(4)), nested_size)

    def read_from_debugger(self) -> bytearray:
        return b"".join(
            [container.read_from_debugger() for container in self.__nested_containers]
        )

    @staticmethod
    def formatter_compatible():
        return False

    @staticmethod
    def is_nested() -> bool:
        return True


class RustVectorAny2D(Container2D):
    # LLDB type syntac: type[size]
    # GBD type syntax: [type; size]
    __REGEX = rf"^(?:mut\s)?alloc::vec::Vec<(.*),.*>$"

    def __init__(self, dbg_value: AbstractValue, name: str, dims=[]):
        typename = dbg_value.typename()
        sample_type = self._parse_typename(typename)[0]
        self.__vector = RustVector(dbg_value)
        self.__nested_dim = dims
        super().__init__(dbg_value, name, sample_type)

        # Try to build the nested containers
        assert self.__nested_containers is not None

    @property
    def size(self) -> int:
        return self.__vector.size

    @property
    def __nested_containers(self) -> List[Container1D]:
        return self._nested_containers(
            self.__vector.data_ptr_value(), self.size, self.__nested_dim
        )

    def shape(self) -> Tuple[int, int]:
        return (
            self.size,
            self.__nested_containers[0].size,
        )

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @classmethod
    def _parse_typename(
        cls, typename: str, **_
    ) -> Tuple[SampleType, int, Optional[int]]:
        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"RustVectorAny2D could not parse {typename} as a valid Rust vector type"
            )

        # Check if contains a nested valid 1D container
        nested_typename = re_match.group(1)
        nested = EntityFactory().check_valid_simple(nested_typename)
        if nested is None or not issubclass(nested, Container1D):
            raise TypeError(
                f"RustVectorAny2D could not parse nested type {nested_typename} as a valid Container1D type"
            )

        sample_type, nested_size = nested.parse_typename(nested_typename)
        return (sample_type, None, nested_size)

    def read_from_debugger(self) -> bytearray:
        if self.size <= 0:
            raise DebuggerMemoryError("Vector size is <= 0")
        return b"".join(
            [container.read_from_debugger() for container in self.__nested_containers]
        )

    @staticmethod
    def formatter_compatible():
        return False

    @staticmethod
    def is_nested() -> bool:
        return True


class RustSliceAny2D(Container2D):
    __REGEX = rf"^&\s?(?:mut\s?)?\[(.*)]$"

    def __init__(self, dbg_value: AbstractValue, name: str, dims=[]):
        typename = dbg_value.typename()
        sample_type = self._parse_typename(typename)[0]
        self.__slice = RustSlice(dbg_value)
        self.__nested_dim = dims
        super().__init__(dbg_value, name, sample_type)

        # Try to build the nested containers
        assert self.__nested_containers is not None

    @property
    def size(self) -> int:
        return self.__slice.size

    @property
    def __nested_containers(self) -> List[Container1D]:
        return self._nested_containers(
            self.__slice.data_ptr_value(), self.size, self.__nested_dim
        )

    def shape(self) -> Tuple[int, int]:
        return (
            self.size,
            self.__nested_containers[0].size,
        )

    @staticmethod
    def name_parser(typename: str) -> bool:
        pattern = re.compile(RustSliceAny2D.__REGEX)
        matched = pattern.match(typename)
        if matched is not None:
            inner = matched.group(1)
            return EntityFactory().check_valid_simple(inner) is not None
        return False

    @classmethod
    def typename_matcher(cls) -> Callable[[str], bool]:
        return RustSliceAny2D.name_parser

    @classmethod
    def _parse_typename(
        cls, typename: str, **_
    ) -> Tuple[SampleType, int, Optional[int]]:
        re_match = re.compile(RustSliceAny2D.__REGEX).match(typename)
        if re_match is None:
            raise TypeError(
                f"RustSliceAny2D could not parse {typename} as a valid Rust vector type"
            )

        # Check if contains a nested valid 1D container
        nested_typename = re_match.group(1)
        nested = EntityFactory().check_valid_simple(nested_typename)
        if nested is None or not issubclass(nested, Container1D):
            raise TypeError(
                f"RustSliceAny2D could not parse nested type {nested_typename} as a valid Container1D type"
            )

        sample_type, nested_size = nested.parse_typename(nested_typename)
        return (sample_type, None, nested_size)

    def read_from_debugger(self) -> bytearray:
        if self.size <= 0:
            raise DebuggerMemoryError("Slice size is <= 0")
        return b"".join(
            [container.read_from_debugger() for container in self.__nested_containers]
        )

    @staticmethod
    def formatter_compatible():
        return False

    @staticmethod
    def is_nested() -> bool:
        return True


RustArrayArray2D.register(LanguageType.RUST)
RustArrayAny2D.register(LanguageType.RUST)
RustVectorAny2D.register(LanguageType.RUST)
RustSliceAny2D.register(LanguageType.RUST)
