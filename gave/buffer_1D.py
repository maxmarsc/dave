from abc import ABC, abstractmethod
from enum import Enum
import re
import gdb  # type: ignore
import gdb.types  # type: ignore


class FloatingPointType(Enum):
    FLOAT = "float"
    DOUBLE = "double"

    def byte_size(self) -> int:
        if self == FloatingPointType.FLOAT:
            return 4
        else:
            return 8


class Buffer1D(ABC):
    def __init__(self, gdb_value: gdb.Value, name: str) -> None:
        super().__init__()
        self._value = gdb_value
        self._name = name

    @classmethod
    @abstractmethod
    def regex_name(cls) -> re.Pattern:
        pass

    @property
    @abstractmethod
    def float_type(self) -> FloatingPointType:
        pass

    @property
    def name(self) -> str:
        return self._name

    @property
    @abstractmethod
    def size(self) -> int:
        pass

    @property
    def byte_size(self) -> int:
        return self.size * self.float_type.byte_size()

    @abstractmethod
    def data(self) -> int:
        pass


class CArray1D(Buffer1D):
    __REGEX = r"^(?:const\s+)?(float|double)\s*\[(\d+)\]$"

    def __init__(self, gdb_value: gdb.Value, name: str):
        super().__init__(gdb_value, name)
        re_match = self.regex_name().match(str(gdb_value.type))
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

    def data(self) -> int:
        ptr_type = gdb.lookup_type(self.float_type.value).pointer().const()
        return int(self._value.cast(ptr_type))
