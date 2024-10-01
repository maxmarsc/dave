from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import re
from typing import Any, Callable, List, Tuple, Type, Union

from dave.common.data_layout import DataLayout
from dave.common.sample_type import SampleType
from dave.common.raw_container import RawContainer

from .debuggers.value import AbstractValue


class Container(ABC):
    __count = -1

    @staticmethod
    def __new_id() -> int:
        Container.__count += 1
        return Container.__count

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

    def as_raw(self) -> RawContainer:
        return RawContainer(
            self.id,
            self.read_from_debugger(),
            self.name,
            self.shape(),
            self.dimensions_fixed(),
            self.float_type,
            type(self),
            self.default_layout(),
            self.available_data_layouts()
        )

    @property
    def float_type(self) -> SampleType:
        return self.__type

    # @property
    # def dtype(self) -> np.dtype:
    #     return self.__type.numpy_type()

    @abstractmethod
    def shape(self) -> Tuple[int, int]:
        pass

    @staticmethod
    @abstractmethod
    def available_data_layouts() -> List[DataLayout]:
        pass

    @staticmethod
    @abstractmethod
    def dimensions_fixed() -> bool:
        pass

    @abstractmethod
    def default_layout() -> DataLayout:
        pass

    @abstractmethod
    def read_from_debugger(self) -> bytearray:
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
  
    @staticmethod
    def dimensions_fixed() -> bool:
        return False


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
    
    @staticmethod
    def dimensions_fixed() -> bool:
        return True
