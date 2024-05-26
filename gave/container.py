from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import re
from typing import List, Tuple, Type

from .data_layout import DataLayout
import numpy as np
import gdb  # type: ignore
import uuid


class SampleType(Enum):
    FLOAT = "float"
    DOUBLE = "double"
    CPX_F = "complex float"
    CPX_D = "complex double"

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

    def dtype(self) -> np.dtype:
        return {
            SampleType.FLOAT: np.float32,
            SampleType.DOUBLE: np.float64,
            SampleType.CPX_F: np.complex64,
            SampleType.CPX_D: np.complex128,
        }[self]

    def is_complex(self) -> bool:
        if self in (SampleType.CPX_F, SampleType.CPX_D):
            return True
        return False


class ChannelSetup(Enum):
    MONO = "mono"
    MULTI_KNOWN = "multi_known"
    MULTI_UNKNOWN = "multi_unknown"


class Container(ABC):
    @dataclass
    class Raw:
        id: uuid.uuid4
        data: np.ndarray
        name: str
        container_cls: Type
        default_layout: DataLayout

    def __init__(self, gdb_value: gdb.Value, name: str) -> None:
        self._value = gdb_value
        self._name = name
        self.__uuid = uuid.uuid4()

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> uuid.uuid4:
        return self.__uuid

    def as_raw(self) -> Raw:
        return Container.Raw(
            self.id, self.read_from_gdb(), self.name, type(self), self.default_layout()
        )

    @classmethod
    @abstractmethod
    def regex_name(cls) -> re.Pattern:
        pass

    @property
    @abstractmethod
    def float_type(self) -> SampleType:
        pass

    @property
    @abstractmethod
    def dtype(self) -> np.dtype:
        pass

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
    def read_from_gdb(self) -> np.ndarray:
        pass
