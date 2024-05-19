from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import re
from typing import List, Tuple, Type

from .data_layout import DataLayout
import numpy as np
import gdb  # type: ignore
import uuid


class FloatingPointType(Enum):
    FLOAT = "float"
    DOUBLE = "double"

    def byte_size(self) -> int:
        if self == FloatingPointType.FLOAT:
            return 4
        else:
            return 8


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
        shape: Tuple[int, int]

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
            self.id, self.read_from_gdb(), self.name, type(self), self.shape()
        )

    @classmethod
    @abstractmethod
    def regex_name(cls) -> re.Pattern:
        pass

    @property
    @abstractmethod
    def float_type(self) -> FloatingPointType:
        pass

    @abstractmethod
    def shape(self) -> Tuple[int, int]:
        pass

    @staticmethod
    @abstractmethod
    def available_data_layouts(self) -> List[DataLayout]:
        pass

    @abstractmethod
    def read_from_gdb(self) -> np.ndarray:
        pass
