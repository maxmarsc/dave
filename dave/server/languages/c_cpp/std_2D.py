from __future__ import annotations

# from abc import ABC, abstractmethod
# from enum import Enum
import re
from typing import Callable, List, Optional, Tuple
from pathlib import Path

from dave.common.logger import Logger

# import gdb  # type: ignore
# import gdb.types  # type: ignore

from ...container import Container, Container1D, SampleType, Container2D
from ...entity_factory import EntityFactory
from ...debuggers.value import AbstractValue, DebuggerMemoryError

from .std_base import StdVector, StdSpan
from .template_parser import parse_template


class CArrayAny2D(Container2D):
    """
    Match any C table of containers, except for 2D C table. These should match
    CarrayC2D
    """

    __REGEX = rf"^(?:const\s+)?([^[\]]*)\s*\[(\d+)\]$"

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
                f"CArrayAny2D could not parse {typename} as a valid C array type"
            )

        # Check if contains a nested valid 1D container
        nested_typename = re_match.group(1)
        nested = EntityFactory().check_valid_simple(nested_typename)
        if nested is None or not issubclass(nested, Container1D):
            raise TypeError(
                f"CArrayAny2D could not parse nested type {nested_typename} as a valid Container1D type"
            )

        sample_type, nested_size = nested.parse_typename(nested_typename)

        return (sample_type, int(re_match.group(2)), nested_size)

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


class CarrayCarray2D(Container2D):
    """
    Match 2D C table of float values
    """

    __REGEX = rf"^(?:const\s+)?{SampleType.regex()}\s*\[(\d+)\]\s*\[(\d+)\]$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
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
                f"CarrayCarray2D could not parse {typename} as a valid 2D C array type"
            )

        return (
            SampleType.parse(re_match.group(1)),
            int(re_match.group(2)),
            int(re_match.group(3)),
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


class Pointer2D(Container2D):
    """
    Match any ptr of containers
    """

    __REGEX = rf"^(?:const\s+)?(.*)\s*\*$"

    def __init__(self, dbg_value: AbstractValue, name: str, dims: List[int]):
        typename = dbg_value.typename()
        sample_type, self.__size, _ = self._parse_typename(typename, dims=dims)

        self._value = dbg_value
        self.__dims = dims
        super().__init__(dbg_value, name, sample_type)

        # Try to build the nested containers
        assert self.__nested_containers is not None

    @property
    def __nested_containers(self) -> List[Container1D]:
        return self._nested_containers(self._value, self.__dims[0], self.__dims[1:])

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
        cls, typename: str, **kwargs
    ) -> Tuple[SampleType, Optional[int], Optional[int]]:
        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"Pointer2D could not parse {typename} as a valid ptr to container type"
            )

        # Check if contains a nested valid 1D container
        nested_typename = re_match.group(1)
        nested = EntityFactory().check_valid_simple(nested_typename)
        if nested is None or not issubclass(nested, Container1D):
            raise TypeError(
                f"Pointer2D could not parse nested type {nested_typename} as a valid container type"
            )

        # Check for provided dimensions
        dims = kwargs["dims"]
        if "*" in nested_typename and len(dims) != 2:
            raise TypeError(
                "Pointer of pointer container requires exactly two dimensions"
            )
        elif not "*" in nested_typename and len(dims) != 1:
            raise TypeError("Pointer container requires exactly one dimension")

        sample_type, nested_size = nested.parse_typename(nested_typename)
        return (sample_type, dims[0], nested_size)

    def read_from_debugger(self) -> bytearray:
        nested_containers = self.__nested_containers
        if self.__size <= 0 or nested_containers[0].size <= 0:
            raise DebuggerMemoryError("A dimension is <= 0")
        return b"".join(
            [container.read_from_debugger() for container in nested_containers]
        )

    @staticmethod
    def formatter_compatible():
        return False

    @staticmethod
    def is_nested() -> bool:
        return True


class StdArray2D(Container2D):
    __REGEX = rf"^(?:const\s+)?std::(?:\_\_1\:\:)?array<(.*),\s*(\d+)[a-z]*>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, dims=[]):
        typename = dbg_value.typename()
        sample_type, self.__size, _ = self._parse_typename(typename)
        self._value = dbg_value
        self.__nested_dim = dims
        super().__init__(dbg_value, name, sample_type)

        # Try to build the nested containers
        assert self.__nested_containers is not None

    @property
    def __nested_containers(self) -> List[Container1D]:
        return self._nested_containers(
            self.__data_ptr_value(), self.__size, self.__nested_dim
        )

    def shape(self) -> Tuple[int, int]:
        return (self.__size, self.__nested_containers[0].size)

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
                f"StdArray2D could not parse {typename} as a valid std::array type"
            )

        # Check if contains a nested valid 1D container
        nested_typename = re_match.group(1)
        nested = EntityFactory().check_valid_simple(nested_typename)
        if nested is None or not issubclass(nested, Container1D):
            raise TypeError(
                f"StdArray2D could not parse nested type {nested_typename} as a valid container type"
            )

        sample_type, nested_size = nested.parse_typename(nested_typename)
        return (sample_type, int(re_match.group(2)), nested_size)

    def __data_ptr_value(self) -> AbstractValue:
        assert isinstance(self._value, AbstractValue)

        # via libstdc++ (GNU) members
        try:
            return self._value.attr("_M_elems")
        except RuntimeError:
            pass

        # via libc++ (LLVM) members
        try:
            return self._value.attr("__elems_")
        except RuntimeError:
            pass

        raise RuntimeError(
            f"Failed to retrieve data ptr of {self._value.typename()}. "
            "Consider disabling optimization or use a supported stdlib version"
        )

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


class StdVector2D(Container2D):
    def __init__(self, dbg_value: AbstractValue, name: str, dims=[]):
        typename = dbg_value.typename()
        sample_type, *_ = self._parse_typename(typename)
        self._value = dbg_value
        self.__vec = StdVector(dbg_value)
        self.__nested_dim = dims
        super().__init__(dbg_value, name, sample_type)

        # Try to build the nested containers
        assert self.__nested_containers is not None

    @property
    def size(self) -> int:
        return self.__vec.size

    @property
    def __nested_containers(self) -> List[Container1D]:
        return self._nested_containers(
            self.__data_ptr_value(), self.size, self.__nested_dim
        )

    def __data_ptr_value(self) -> AbstractValue:
        return self.__vec.data_ptr_value()

    def shape(self) -> Tuple[int, int]:
        return (
            self.size,
            self.__nested_containers[0].size,
        )

    @classmethod
    def typename_matcher(cls) -> Callable[[str], bool]:
        return StdVector2D.name_parser

    @classmethod
    def _parse_typename(
        cls, typename: str, **_
    ) -> Tuple[SampleType, Optional[int], Optional[int]]:
        parsed_types = parse_template(typename)
        if not StdVector2D.name_parser(typename):
            raise TypeError(
                f"StdVector2D could not parse {typename} as a valid std::vector type"
            )

        # Check if contains a nested valid 1D container
        nested_typename = parsed_types[1]
        nested = EntityFactory().check_valid_simple(nested_typename)
        if nested is None or not issubclass(nested, Container1D):
            raise TypeError(
                f"StdVector2D could not parse nested type {nested_typename} as a valid container type"
            )

        sample_type, nested_size = nested.parse_typename(nested_typename)
        return (sample_type, None, nested_size)

    @staticmethod
    def name_parser(typename: str) -> bool:
        types = parse_template(typename)
        if types[0].strip() == "std::vector" and len(types) == 3:
            return True
        return False

    def read_from_debugger(self) -> bytearray:
        if self.size <= 0:
            raise DebuggerMemoryError("std::vector size is <= 0")
        return b"".join(
            [container.read_from_debugger() for container in self.__nested_containers]
        )

    @staticmethod
    def formatter_compatible():
        return False

    @staticmethod
    def is_nested() -> bool:
        return True


class StdSpan2D(Container2D):
    __REGEX = rf"^(?:const\s+)?(?:std|gsl)::(?:\_\_1\:\:)?span<(?:const)?\s*(.*)\s*(?:const)?,\s*(\d+)[a-z]*>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, dims=[]):
        typename = dbg_value.typename()
        sample_type, size, _ = self._parse_typename(typename)
        self.__span = StdSpan(dbg_value, size)
        self._value = dbg_value
        self.__nested_dim = dims
        super().__init__(dbg_value, name, sample_type)

        # Try to build the nested containers
        assert self.__nested_containers is not None

    @property
    def size(self) -> int:
        return self.__span.size

    @property
    def __nested_containers(self) -> List[Container1D]:
        return self._nested_containers(
            self.__data_ptr_value(), self.size, self.__nested_dim
        )

    def __data_ptr_value(self) -> AbstractValue:
        return self.__span.data_ptr_value()

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
                f"StdSpan2D could not parse {typename} as a valid span type"
            )

        # Check if contains a nested valid 1D container
        nested_typename = re_match.group(1)
        nested = EntityFactory().check_valid_simple(nested_typename)
        if nested is None or not issubclass(nested, Container1D):
            raise TypeError(
                f"StdSpan2D could not parse nested type {nested_typename} as a valid Container1D type"
            )

        sample_type, nested_size = nested.parse_typename(nested_typename)
        return (sample_type, int(re_match.group(2)), nested_size)

    def read_from_debugger(self) -> bytearray:
        if self.size <= 0:
            raise DebuggerMemoryError("std::span size is <= 0")
        return b"".join(
            [container.read_from_debugger() for container in self.__nested_containers]
        )

    @staticmethod
    def formatter_compatible():
        return False

    @staticmethod
    def is_nested() -> bool:
        return True


CArrayAny2D.register()
CarrayCarray2D.register()
Pointer2D.register()
StdArray2D.register()
StdVector2D.register()
StdSpan2D.register()
