from abc import ABC, abstractmethod
from enum import Enum
import re
from typing import List, Tuple
import gdb  # type: ignore
import gdb.types  # type: ignore
import numpy as np


from .container import FloatingPointType, Container
from .container_factory import ContainerFactory
from .data_layout import DataLayout


# class Container1D(Container):
#     def __init__(self, gdb_value: gdb.Value, name: str) -> None:
#         super().__init__(gdb_value, name)

#     @property
#     @abstractmethod
#     def size(self) -> int:
#         pass

#     @property
#     def byte_size(self) -> int:
#         return self.size * self.float_type.byte_size()

#     @staticmethod
#     def available_data_layouts() -> List[DataLayout]:
#         return [DataLayout.REAL_1D]


class ScalarCArray1D(Container):
    __REGEX = r"^(?:const\s+)?(float|double)\s*\[(\d+)\]$"

    def __init__(self, gdb_value: gdb.Value, name: str):
        super().__init__(gdb_value, name)
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(f"{gdb_value.type} is not a valid CArray type")

        self.__type = FloatingPointType(re_match.group(1))
        self.__size = int(re_match.group(2))

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @property
    def float_type(self) -> FloatingPointType:
        return self.__type

    @property
    def size(self) -> int:
        return self.__size

    @property
    def byte_size(self) -> int:
        return self.size * self.float_type.byte_size()

    def shape(self) -> Tuple[int, int]:
        return (1, self.size)

    @staticmethod
    def available_data_layouts() -> List[DataLayout]:
        return [
            DataLayout.REAL_1D,
            DataLayout.REAL_2D,
            DataLayout.CPX_1D,
            DataLayout.CPX_2D,
        ]

    def read_from_gdb(self) -> np.ndarray:
        ptr_type = gdb.lookup_type(self.float_type.value).pointer().const()
        ptr = int(self._value.cast(ptr_type))
        inferior = gdb.selected_inferior()
        dtype = np.float32
        array = np.frombuffer(inferior.read_memory(ptr, self.byte_size), dtype=dtype)
        print(f"dtype : {array.dtype}")
        print(f"shape : {array.shape}")
        # print(f"array : {array}")
        return array.reshape(self.shape())


class ComplexCArray1D(Container):
    __REGEX = r"^(?:const\s+)?(?:complex\s+)(float|double)\s*\[(\d+)\]$"

    def __init__(self, gdb_value: gdb.Value, name: str):
        super().__init__(gdb_value, name)
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(f"{gdb_value.type} is not a valid ComplexCArray1D type")

        self.__type = FloatingPointType(re_match.group(1))
        self.__size = int(re_match.group(2))

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @property
    def float_type(self) -> FloatingPointType:
        return self.__type

    @property
    def size(self) -> int:
        return self.__size

    def shape(self) -> Tuple[int, int]:
        return (1, self.size)

    @property
    def byte_size(self) -> int:
        return self.size * self.float_type.byte_size() * 2

    @staticmethod
    def available_data_layouts() -> List[DataLayout]:
        return [
            DataLayout.CPX_1D,
            DataLayout.CPX_2D,
            DataLayout.REAL_1D,
            DataLayout.REAL_2D,
        ]

    def read_from_gdb(self) -> np.ndarray:
        ptr_type = gdb.lookup_type("complex " + self.float_type.value).pointer().const()
        ptr = int(self._value.cast(ptr_type))
        inferior = gdb.selected_inferior()
        dtype = np.complex64
        array = np.frombuffer(inferior.read_memory(ptr, self.byte_size), dtype=dtype)
        print(f"dtype : {array.dtype}")
        print(f"shape : {array.shape}")
        # print(f"array : {array}")
        return array.reshape(self.shape())


ContainerFactory().register(ScalarCArray1D)
ContainerFactory().register(ComplexCArray1D)
