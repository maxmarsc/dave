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


class CArray1D(Container):
    __REGEX = r"^(?:const\s+)?(complex\s+)?(float|double)\s*\[(\d+)\]$"

    def __init__(self, gdb_value: gdb.Value, name: str):
        super().__init__(gdb_value, name)
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(f"{gdb_value.type} is not a valid CArray1D type")

        self.__complex = bool(re_match.group(1))
        self.__type = FloatingPointType(re_match.group(2))
        self.__size = int(re_match.group(3))

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @property
    def float_type(self) -> FloatingPointType:
        return self.__type

    @property
    def dtype(self) -> np.dtype:
        if self.float_type == FloatingPointType.FLOAT:
            if self.__complex:
                return np.complex64
            else:
                return np.float32
        else:
            #
            if self.__complex:
                return np.complex128
            else:
                return np.float64

    @property
    def size(self) -> int:
        return self.__size

    def shape(self) -> Tuple[int, int]:
        return (1, self.size)

    @property
    def byte_size(self) -> int:
        if self.__complex:
            return self.size * self.float_type.byte_size() * 2
        else:
            return self.size * self.float_type.byte_size()

    def default_layout(self) -> DataLayout:
        if self.__complex:
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
        str_type = self.float_type.value
        if self.__complex:
            str_type = "complex " + str_type
        ptr_type = gdb.lookup_type(str_type).pointer().const()
        ptr = int(self._value.cast(ptr_type))
        inferior = gdb.selected_inferior()
        array = np.frombuffer(
            inferior.read_memory(ptr, self.byte_size), dtype=self.dtype
        )
        print(f"dtype : {array.dtype}")
        print(f"shape : {array.shape}")
        # print(f"array : {array}")
        return array.reshape(self.shape())


ContainerFactory().register(CArray1D)
