from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum


class Endianness(Enum):
    LITTLE = "<"
    BIG = ">"


class AbstractValue(ABC):
    @abstractmethod
    def typename(self) -> str:
        pass

    @abstractmethod
    def byte_size(self) -> int:
        pass

    @abstractmethod
    def attr(self, name: str) -> AbstractValue:
        pass

    @abstractmethod
    def address(self) -> int:
        pass

    @abstractmethod
    def __int__(self) -> int:
        pass

    @abstractmethod
    def __float__(self) -> float:
        pass

    @abstractmethod
    def __getitem__(self, key: int) -> AbstractValue:
        pass

    @abstractmethod
    def in_scope(self) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def readmemory(addr: int, bytesize: int) -> bytearray:
        pass
