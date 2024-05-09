from abc import ABC, abstractmethod
from enum import Enum
import re
from typing import List

from .data_model import DataModel
import numpy as np
import gdb


class FloatingPointType(Enum):
    FLOAT = "float"
    DOUBLE = "double"

    def byte_size(self) -> int:
        if self == FloatingPointType.FLOAT:
            return 4
        else:
            return 8


class Container(ABC):
    def __init__(self, gdb_value: gdb.Value, name: str) -> None:
        self._value = gdb_value
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @classmethod
    @abstractmethod
    def regex_name(cls) -> re.Pattern:
        pass

    @property
    @abstractmethod
    def float_type(self) -> FloatingPointType:
        pass

    @staticmethod
    @abstractmethod
    def available_data_models(self) -> List[DataModel]:
        pass

    @abstractmethod
    def read_from_gdb(self) -> np.ndarray:
        pass
