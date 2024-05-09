from abc import ABC, abstractmethod
from enum import Enum
import re


class FloatingPointType(Enum):
    FLOAT = "float"
    DOUBLE = "double"

    def byte_size(self) -> int:
        if self == FloatingPointType.FLOAT:
            return 4
        else:
            return 8


class Buffer(ABC):
    @classmethod
    @abstractmethod
    def regex_name(cls) -> re.Pattern:
        pass

    @property
    @abstractmethod
    def float_type(self) -> FloatingPointType:
        pass
