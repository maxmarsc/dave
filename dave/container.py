from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import re
from typing import Any, Callable, List, Tuple, Type, Union

from .data_layout import DataLayout

from .debuggers.value import AbstractValue

import numpy as np

# import gdb  # type: ignore
# import uuid


class SampleType(Enum):
    FLOAT = "float"
    DOUBLE = "double"
    CPX_F = "complex float"
    CPX_D = "complex double"

    @staticmethod
    def regex() -> str:
        return r"(float|double|complex\s+float|complex\s+double|std::complex<float>|std::complex<double>)"

    @staticmethod
    def parse(name: str):
        if name == "std::complex<float>":
            return SampleType("complex float")
        elif name == "std::complex<double>":
            return SampleType("complex double")
        else:
            return SampleType(name)

    def byte_size(self) -> int:
        return {
            SampleType.FLOAT: 4,
            SampleType.DOUBLE: 8,
            SampleType.CPX_F: 8,
            SampleType.CPX_D: 16,
        }[self]

    def numpy_type(self) -> np.dtype:
        return {
            SampleType.FLOAT: np.float32,
            SampleType.DOUBLE: np.float64,
            SampleType.CPX_F: np.complex64,
            SampleType.CPX_D: np.complex128,
        }[self]

    @staticmethod
    def from_numpy(dtype: np.dtype):
        return {
            np.float32: SampleType.FLOAT,
            np.float64: SampleType.DOUBLE,
            np.complex64: SampleType.CPX_F,
            np.complex128: SampleType.CPX_D,
        }[dtype.type]

    def gdb_type(self):
        import gdb  # type: ignore

        return gdb.lookup_type(self.value)

    def is_complex(self) -> bool:
        if self in (SampleType.CPX_F, SampleType.CPX_D):
            return True
        return False


class ChannelSetup(Enum):
    MONO = "mono"
    MULTI_KNOWN = "multi_known"
    MULTI_UNKNOWN = "multi_unknown"


class Container(ABC):
    __count = -1

    @staticmethod
    def __new_id() -> int:
        Container.__count += 1
        return Container.__count

    @dataclass
    class Raw:
        id: int
        data: np.ndarray
        name: str
        container_cls: Type
        default_layout: DataLayout

    def __init__(self, dbg_value: Any, name: str, data_type: SampleType) -> None:
        self._value = dbg_value
        self._name = name
        self.__type = data_type
        self.__id = Container.__new_id()

    @property
    def name(self) -> str:
        return self._name

    @property
    def in_scope(self) -> bool:
        if isinstance(self._value, AbstractValue):
            return self._value.in_scope()
        return True

    @property
    def id(self) -> int:
        return self.__id

    def as_raw(self) -> Raw:
        return Container.Raw(
            self.id,
            self.read_from_debugger(),
            self.name,
            type(self),
            self.default_layout(),
        )

    @property
    def float_type(self) -> SampleType:
        return self.__type

    @property
    def dtype(self) -> np.dtype:
        return self.__type.numpy_type()

    @abstractmethod
    def shape(self) -> Tuple[int, int]:
        pass

    @staticmethod
    @abstractmethod
    def available_data_layouts() -> List[DataLayout]:
        pass

    @abstractmethod
    def default_layout() -> DataLayout:
        pass

    @abstractmethod
    def read_from_debugger(self) -> np.ndarray:
        pass

    @classmethod
    @abstractmethod
    def typename_matcher(cls) -> Union[re.Pattern, Callable[[str], bool]]:
        pass


class Container1D(Container):
    def __init__(self, dbg_value: Any, name: str, data_type: SampleType) -> None:
        super().__init__(dbg_value, name, data_type)

    @property
    @abstractmethod
    def size(self) -> int:
        pass

    def shape(self) -> Tuple[int, int]:
        return (1, self.size)

    @property
    def byte_size(self) -> int:
        return self.float_type.byte_size() * self.size

    def default_layout(self) -> DataLayout:
        if self.float_type.is_complex():
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


class Container2D(Container):
    def __init__(self, dbg_value: Any, name: str, data_type: SampleType) -> None:
        super().__init__(dbg_value, name, data_type)

    def default_layout(self) -> DataLayout:
        if self.float_type.is_complex():
            return DataLayout.CPX_2D
        else:
            return DataLayout.REAL_2D

    @staticmethod
    def available_data_layouts() -> List[DataLayout]:
        return [
            DataLayout.CPX_2D,
            DataLayout.REAL_2D,
        ]
