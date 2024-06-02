from abc import ABC, abstractmethod
from enum import Enum
import re
from typing import List, Tuple
import gdb  # type: ignore
import gdb.types  # type: ignore
import numpy as np


from .container import SampleType, Container, Container1D
from .container_factory import ContainerFactory
from .data_layout import DataLayout


class CArray1D(Container1D):
    __REGEX = rf"^(?:const\s+)?{SampleType.regex()}\s*\[(\d+)\]$"

    def __init__(self, gdb_value: gdb.Value, name: str, _):
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(f"Could not parse {gdb_value.type} as a valid C array type")

        data_type = SampleType.parse(re_match.group(1))
        size = int(re_match.group(2))
        super().__init__(gdb_value, name, data_type, size)

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_from_gdb(self) -> np.ndarray:
        inferior = gdb.selected_inferior()
        array = np.frombuffer(
            inferior.read_memory(self._value.address, self.byte_size), dtype=self.dtype
        )
        return array.reshape(self.shape())


class Pointer(Container1D):
    __REGEX = rf"^(?:const\s+)?{SampleType.regex()}\s*\*$"

    def __init__(self, gdb_value: gdb.Value, name: str, dims: List[int]):
        print(dims)
        if len(dims) != 1:
            raise gdb.GdbError("Pointer container requires exactly one dimension")
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(f"Could not parse {gdb_value.type} as a valid C array type")

        data_type = SampleType.parse(re_match.group(1))
        size = dims[0]
        super().__init__(gdb_value, name, data_type, size)

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_from_gdb(self) -> np.ndarray:
        inferior = gdb.selected_inferior()
        array = np.frombuffer(
            inferior.read_memory(self._value, self.byte_size), dtype=self.dtype
        )
        return array.reshape(self.shape())


class StdArray(Container1D):
    __REGEX = rf"^(?:const\s+)?std::array<{SampleType.regex()},\s*(\d+)>\s*$"

    def __init__(self, gdb_value: gdb.Value, name: str, _):
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {gdb_value.type} as a valid std::array type"
            )

        data_type = SampleType.parse(re_match.group(1))
        size = int(re_match.group(2))
        super().__init__(gdb_value, name, data_type, size)

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_from_gdb(self) -> np.ndarray:
        inferior = gdb.selected_inferior()
        array = np.frombuffer(
            inferior.read_memory(self._value.address, self.byte_size), dtype=self.dtype
        )
        return array.reshape(self.shape())


class StdVector(Container1D):
    __REGEX = rf"^(?:const\s+)?std::vector<{SampleType.regex()},\s*.*<\1\s?>\s*>\s*$"

    def __init__(self, gdb_value: gdb.Value, name: str, _):
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {gdb_value.type} as a valid std::vector type"
            )

        datatype = SampleType.parse(re_match.group(1))
        size = self.read_size(gdb_value)
        super().__init__(gdb_value, name, datatype, size)

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_size(self, gdb_val: gdb.Value = None) -> int:
        if gdb_val is None:
            gdb_val = self._value
        return int(gdb_val["_M_impl"]["_M_finish"] - gdb_val["_M_impl"]["_M_start"])

    def read_from_gdb(self) -> np.ndarray:
        inferior = gdb.selected_inferior()
        data_ptr = self._value["_M_impl"]["_M_start"]
        array = np.frombuffer(
            inferior.read_memory(data_ptr, self.byte_size), dtype=self.dtype
        )
        return array.reshape(self.shape())


class StdSpan(Container1D):
    __REGEX = rf"^(?:const\s+)?std::span<{SampleType.regex()},\s*(\d+)>\s*$"

    def __init__(self, gdb_value: gdb.Value, name: str, _):
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {gdb_value.type} as a valid std::span type"
            )

        self.__extent = int(re_match.group(2))
        datatype = SampleType.parse(re_match.group(1))
        size = self.read_size(gdb_value)
        super().__init__(gdb_value, name, datatype, size)

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_size(self, gdb_val: gdb.Value = None) -> int:
        if gdb_val is None:
            gdb_val = self._value
        if self.__extent != 18446744073709551615:
            return self.__extent
        else:
            return int(gdb_val["_M_extent"]["_M_extent_value"])

    def read_from_gdb(self) -> np.ndarray:
        inferior = gdb.selected_inferior()
        data_ptr = self._value["_M_ptr"]
        array = np.frombuffer(
            inferior.read_memory(data_ptr, self.byte_size), dtype=self.dtype
        )
        return array.reshape(self.shape())


ContainerFactory().register(CArray1D)
ContainerFactory().register(StdArray)
ContainerFactory().register(StdVector)
ContainerFactory().register(StdSpan)
ContainerFactory().register(Pointer)
