from __future__ import annotations

# from abc import ABC, abstractmethod
# from enum import Enum
import re
from typing import Callable, List, Tuple
from pathlib import Path

# import gdb  # type: ignore
# import gdb.types  # type: ignore

from ...container import SampleType, Container2D
from ...container_factory import ContainerFactory
from ...debuggers.value import AbstractValue

from .std_base import StdVector, StdSpan
from .template_parser import parse_template


class CArrayAny2D(Container2D):
    """
    Match any C table of containers, except for 2D C table. These should match
    CarrayC2D
    """

    __REGEX = rf"^(?:const\s+)?([^[\]]*)\s*\[(\d+)\]$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"CArrayAny2D could not parse {typename} as a valid C array type"
            )

        # Check if contains a nested valid 1D container
        nested = re_match.group(1)
        if not ContainerFactory().check_valid_1D(nested):
            raise TypeError(
                f"CArrayAny2D could not parse nested type {nested} as a valid container type"
            )

        self.__size = int(re_match.group(2))
        self.__nested_containers = [
            ContainerFactory().build_1D(
                dbg_value[i],
                dbg_value[i].typename(),
                "",
                _,
            )
            for i in range(self.__size)
        ]
        super().__init__(dbg_value, name, self.__nested_containers[0].float_type)

    def shape(self) -> Tuple[int, int]:
        return (self.__size, self.__nested_containers[0].size)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_from_debugger(self) -> bytearray:
        return b"".join(
            [container.read_from_debugger() for container in self.__nested_containers]
        )


class CarrayCarray2D(Container2D):
    """
    Match 2D C table of float values
    """

    __REGEX = rf"^(?:const\s+)?{SampleType.regex()}\s*\[(\d+)\]\s*\[(\d+)\]$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"CarrayCarray2D could not parse {typename} as a valid 2D C array type"
            )

        # Check if contains a nested valid 1D container
        data_type = SampleType.parse(re_match.group(1))
        self.__shape = (int(re_match.group(2)), int(re_match.group(3)))
        super().__init__(dbg_value, name, data_type)

    def shape(self) -> Tuple[int, int]:
        return self.__shape

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @property
    def byte_size(self) -> int:
        return self.float_type.byte_size() * self.shape()[0] * self.shape()[1]

    def read_from_debugger(self) -> bytearray:
        assert isinstance(self._value, AbstractValue)
        return self._value.readmemory(self._value.address(), self.byte_size)


class Pointer2D(Container2D):
    """
    Match any ptr of containers
    """

    __REGEX = rf"^(?:const\s+)?(.*)\s*\*$"

    def __init__(self, dbg_value: AbstractValue, name: str, dims: List[int]):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"Pointer2D could not parse {typename} as a valid ptr ptr type"
            )

        # Check if contains a nested valid 1D container
        nested = re_match.group(1)
        if not ContainerFactory().check_valid_1D(nested):
            raise TypeError(
                f"Pointer2D could not parse nested type {nested} as a valid container type"
            )

        if "*" in nested and len(dims) != 2:
            raise TypeError(
                "Pointer of pointer container requires exactly two dimensions"
            )
        elif not "*" in nested and len(dims) != 1:
            raise TypeError("Pointer container requires exactly one dimension")

        self.__size = dims[0]
        self.__nested_containers = [
            ContainerFactory().build_1D(
                dbg_value[i],
                dbg_value[i].typename(),
                "",
                dims[1:],
            )
            for i in range(self.__size)
        ]
        super().__init__(dbg_value, name, self.__nested_containers[0].float_type)

    def shape(self) -> Tuple[int, int]:
        return (self.__size, self.__nested_containers[0].size)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_from_debugger(self) -> bytearray:
        return b"".join(
            [container.read_from_debugger() for container in self.__nested_containers]
        )


class StdArray2D(Container2D):
    __REGEX = rf"^(?:const\s+)?std::(?:\_\_1\:\:)?array<(.*),\s*(\d+)[a-z]*>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"StdArray2D could not parse {typename} as a valid std::array type"
            )

        # Check if contains a nested valid 1D container
        nested = re_match.group(1)
        if not ContainerFactory().check_valid_1D(nested):
            raise TypeError(
                f"StdArray2D could not parse nested type {nested} as a valid container type"
            )

        self.__size = int(re_match.group(2))
        self._value = dbg_value
        self.__nested_containers = [
            ContainerFactory().build_1D(
                self.__data_ptr_value()[i],
                self.__data_ptr_value()[i].typename(),
                "",
                _,
            )
            for i in range(self.__size)
        ]
        super().__init__(dbg_value, name, self.__nested_containers[0].float_type)

    def shape(self) -> Tuple[int, int]:
        return (self.__size, self.__nested_containers[0].size)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

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


class StdVector2D(Container2D):
    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        parsed_types = parse_template(typename)
        if not StdVector2D.name_parser(typename):
            raise TypeError(
                f"StdVector2D could not parse {typename} as a valid std::array type"
            )

        # Check if contains a nested valid 1D container
        nested = parsed_types[1]
        if not ContainerFactory().check_valid_1D(nested):
            raise TypeError(
                f"StdVector2D could not parse nested type {nested} as a valid container type"
            )

        self._value = dbg_value
        self.__vec = StdVector(dbg_value)
        self.__nested_containers = [
            ContainerFactory().build_1D(
                self.__data_ptr_value()[i],
                self.__data_ptr_value()[i].typename(),
                "",
                _,
            )
            for i in range(self.size)
        ]
        super().__init__(dbg_value, name, self.__nested_containers[0].float_type)

    @property
    def size(self) -> int:
        return self.__vec.size

    def __data_ptr_value(self) -> AbstractValue:
        return self.__vec.data_ptr_value()

    def shape(self) -> Tuple[int, int]:
        return (self.size, self.__nested_containers[0].size)

    @classmethod
    def typename_matcher(cls) -> Callable[[str], bool]:
        return StdVector2D.name_parser

    @staticmethod
    def name_parser(typename: str) -> bool:
        types = parse_template(typename)
        if types[0].startswith("std::vector") and len(types) == 3:
            return True
        return False

    def read_from_debugger(self) -> bytearray:
        return b"".join(
            [container.read_from_debugger() for container in self.__nested_containers]
        )


class StdSpan2D(Container2D):
    __REGEX = rf"^(?:const\s+)?(?:std|gsl)::(?:\_\_1\:\:)?span<(.*),\s*(\d+)[a-z]*>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"StdSpan2D could not parse {typename} as a valid std::array type"
            )

        # Check if contains a nested valid 1D container
        nested = re_match.group(1)
        if not ContainerFactory().check_valid_1D(nested):
            raise TypeError(
                f"StdSpan2D could not parse nested type {nested} as a valid container type"
            )

        self.__span = StdSpan(dbg_value, int(re_match.group(2)))
        self._value = dbg_value
        self.__nested_containers = [
            ContainerFactory().build_1D(
                self.__data_ptr_value()[i],
                self.__data_ptr_value()[i].typename(),
                "",
                _,
            )
            for i in range(self.size)
        ]
        super().__init__(dbg_value, name, self.__nested_containers[0].float_type)

    @property
    def size(self) -> int:
        return self.__span.size

    def __data_ptr_value(self) -> AbstractValue:
        return self.__span.data_ptr_value()

    def shape(self) -> Tuple[int, int]:
        return (self.size, self.__nested_containers[0].size)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_from_debugger(self) -> bytearray:
        return b"".join(
            [container.read_from_debugger() for container in self.__nested_containers]
        )


ContainerFactory().register(CArrayAny2D)
ContainerFactory().register(CarrayCarray2D)
ContainerFactory().register(Pointer2D)
ContainerFactory().register(StdArray2D)
ContainerFactory().register(StdVector2D)
ContainerFactory().register(StdSpan2D)
