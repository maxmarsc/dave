from abc import ABC, abstractmethod
from enum import Enum
import re
from typing import List, Tuple
import gdb  # type: ignore
import gdb.types  # type: ignore
import numpy as np


from .container import SampleType, Container
from .container_factory import ContainerFactory
from .data_layout import DataLayout


class CArray1D(Container):
    __REGEX = rf"^(?:const\s+)?{SampleType.regex()}\s*\[(\d+)\]$"

    def __init__(self, gdb_value: gdb.Value, name: str):
        super().__init__(gdb_value, name)
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(f"Could not parse {gdb_value.type} as a valid C array type")

        self.__type = SampleType.parse(re_match.group(1))
        self.__size = int(re_match.group(2))

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @property
    def float_type(self) -> SampleType:
        return self.__type

    @property
    def dtype(self) -> np.dtype:
        return self.__type.numpy_type()

    @property
    def size(self) -> int:
        return self.__size

    def shape(self) -> Tuple[int, int]:
        return (1, self.size)

    @property
    def byte_size(self) -> int:
        return self.__type.byte_size() * self.__size

    def default_layout(self) -> DataLayout:
        if self.__type.is_complex():
            return DataLayout.CPX_1D
        else:
            return DataLayout.REAL_1D

    @staticmethod
    def available_data_layouts() -> List[DataLayout]:
        return [
            DataLayout.CPX_1D,
            DataLayout.CPX_2D,
            DataLayout.REAL_1D,
            DataLayout.REAL_2D,
        ]

    def read_from_gdb(self) -> np.ndarray:
        inferior = gdb.selected_inferior()
        array = np.frombuffer(
            inferior.read_memory(self._value.address, self.byte_size), dtype=self.dtype
        )
        return array.reshape(self.shape())


class StdArray(Container):
    __REGEX = rf"^(?:const\s+)?std::array<{SampleType.regex()},\s*(\d+)>\s*$"

    def __init__(self, gdb_value: gdb.Value, name: str):
        super().__init__(gdb_value, name)
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {gdb_value.type} as a valid std::array type"
            )

        self.__type = SampleType.parse(re_match.group(1))
        self.__size = int(re_match.group(2))

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @property
    def float_type(self) -> SampleType:
        return self.__type

    @property
    def dtype(self) -> np.dtype:
        return self.__type.numpy_type()

    @property
    def size(self) -> int:
        return self.__size

    def shape(self) -> Tuple[int, int]:
        return (1, self.size)

    @property
    def byte_size(self) -> int:
        return self.__type.byte_size() * self.__size

    def default_layout(self) -> DataLayout:
        if self.__type.is_complex():
            return DataLayout.CPX_1D
        else:
            return DataLayout.REAL_1D

    @staticmethod
    def available_data_layouts() -> List[DataLayout]:
        return [
            DataLayout.CPX_1D,
            DataLayout.CPX_2D,
            DataLayout.REAL_1D,
            DataLayout.REAL_2D,
        ]

    def read_from_gdb(self) -> np.ndarray:
        inferior = gdb.selected_inferior()
        array = np.frombuffer(
            inferior.read_memory(self._value.address, self.byte_size), dtype=self.dtype
        )
        return array.reshape(self.shape())


class StdVector(Container):
    __REGEX = rf"^(?:const\s+)?std::vector<{SampleType.regex()},\s*std::allocator<\1\s?>\s*>\s*$"

    def __init__(self, gdb_value: gdb.Value, name: str):
        super().__init__(gdb_value, name)
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {gdb_value.type} as a valid std::vector type"
            )

        self.__type = SampleType.parse(re_match.group(1))
        # self.__size =

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @property
    def float_type(self) -> SampleType:
        return self.__type

    @property
    def dtype(self) -> np.dtype:
        return self.__type.numpy_type()

    @property
    def size(self) -> int:
        return int(
            self._value["_M_impl"]["_M_finish"] - self._value["_M_impl"]["_M_start"]
        )

    def shape(self) -> Tuple[int, int]:
        return (1, self.size)

    @property
    def byte_size(self) -> int:
        return self.__type.byte_size() * self.size

    def default_layout(self) -> DataLayout:
        if self.__type.is_complex():
            return DataLayout.CPX_1D
        else:
            return DataLayout.REAL_1D

    @staticmethod
    def available_data_layouts() -> List[DataLayout]:
        return [
            DataLayout.CPX_1D,
            DataLayout.CPX_2D,
            DataLayout.REAL_1D,
            DataLayout.REAL_2D,
        ]

    def read_from_gdb(self) -> np.ndarray:
        inferior = gdb.selected_inferior()
        data_ptr = self._value["_M_impl"]["_M_start"]
        array = np.frombuffer(
            inferior.read_memory(data_ptr, self.byte_size), dtype=self.dtype
        )
        return array.reshape(self.shape())


class StdSpan(Container):
    __REGEX = rf"^(?:const\s+)?std::span<{SampleType.regex()},\s*(\d+)>\s*$"

    def __init__(self, gdb_value: gdb.Value, name: str):
        super().__init__(gdb_value, name)
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {gdb_value.type} as a valid std::span type"
            )

        self.__type = SampleType.parse(re_match.group(1))
        self.__extent = int(re_match.group(2))

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @property
    def float_type(self) -> SampleType:
        return self.__type

    @property
    def dtype(self) -> np.dtype:
        return self.__type.numpy_type()

    @property
    def size(self) -> int:
        if self.__extent != 18446744073709551615:
            return self.__extent
        else:
            return int(self._value["_M_extent"]["_M_extent_value"])

    def shape(self) -> Tuple[int, int]:
        return (1, self.size)

    @property
    def byte_size(self) -> int:
        return self.__type.byte_size() * self.size

    def default_layout(self) -> DataLayout:
        if self.__type.is_complex():
            return DataLayout.CPX_1D
        else:
            return DataLayout.REAL_1D

    @staticmethod
    def available_data_layouts() -> List[DataLayout]:
        return [
            DataLayout.CPX_1D,
            DataLayout.CPX_2D,
            DataLayout.REAL_1D,
            DataLayout.REAL_2D,
        ]

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
