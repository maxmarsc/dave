from __future__ import annotations
from abc import ABC, abstractmethod
import re
from typing import Any, Callable, List, Tuple, Type, Union
import struct
import cmath

from dave.common.sample_type import SampleType
from dave.common.raw_iir import RawIir

from .debuggers.value import AbstractValue
from .entity import Entity


class IIR(Entity):
    """
    The base class for every IIR filter/coefficients structure

    When implementing a new type of IIR filter support, you need to derive from
    IIR
    """

    def __init__(self, dbg_value: Any, name: str, data_type: SampleType):
        super().__init__(dbg_value, name)
        self.__type = data_type

    @staticmethod
    def formatter_compatible():
        return False

    @staticmethod
    def is_nested() -> bool:
        return False

    def as_raw(self) -> RawIir:
        return RawIir(
            # base
            self.id,
            self.name,
            self.default_layout(),
            self.available_data_layouts(),
            # container
            self.read_from_debugger(),
            self.shape(),
            self.float_type,
        )

    @property
    def float_type(self) -> SampleType:
        return self.__type

    @property
    def byte_size(self) -> int:
        return self.float_type.byte_size() * self.shape()[0] * self.shape()[1]

    @abstractmethod
    def shape(self) -> Tuple[int, int]:
        pass

    @classmethod
    @abstractmethod
    def available_data_layouts(cls) -> List[RawIir.Layout]:
        pass

    @staticmethod
    @abstractmethod
    def default_layout() -> RawIir.Layout:
        pass

    @abstractmethod
    def read_from_debugger(self) -> bytearray:
        pass

    @staticmethod
    def formatter_compatible():
        return False

    @staticmethod
    def support_concat() -> bool:
        return False
