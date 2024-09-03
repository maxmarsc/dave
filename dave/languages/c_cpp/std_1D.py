# from abc import ABC, abstractmethod
# from enum import Enum
import re
from typing import List, Tuple

# import gdb  # type: ignore
# import gdb.types  # type: ignore
import numpy as np


from dave.container import SampleType, Container1D
from dave.container_factory import ContainerFactory
from dave.debuggers.value import AbstractValue


class CArray1D(Container1D):
    __REGEX = rf"^(?:const\s+)?{SampleType.regex()}\s*\[(\d+)\]$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(f"Could not parse {typename} as a valid C array type")

        data_type = SampleType.parse(re_match.group(1))
        self.__size = int(re_match.group(2))
        super().__init__(dbg_value, name, data_type)

    @property
    def size(self) -> int:
        return self.__size

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_from_debugger(self) -> np.ndarray:
        assert isinstance(self._value, AbstractValue)
        array = self._value.readmemory(
            self._value.address(), self.byte_size, self.dtype
        )
        return array.reshape(self.shape())


class Pointer1D(Container1D):
    __REGEX = rf"^(?:const\s+)?{SampleType.regex()}\s*\*$"

    def __init__(self, dbg_value: AbstractValue, name: str, dims: List[int]):
        if len(dims) != 1:
            raise TypeError("Pointer container requires exactly one dimension")
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(f"Could not parse {typename} as a valid C array type")

        data_type = SampleType.parse(re_match.group(1))
        self.__size = dims[0]
        super().__init__(dbg_value, name, data_type)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @property
    def size(self) -> int:
        return self.__size

    def read_from_debugger(self) -> np.ndarray:
        assert isinstance(self._value, AbstractValue)
        array = self._value.readmemory(int(self._value), self.byte_size, self.dtype)
        return array.reshape(self.shape())


class StdArray(Container1D):
    __REGEX = rf"^(?:const\s+)?std::array<{SampleType.regex()},\s*(\d+)>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(f"Could not parse {typename} as a valid std::array type")

        data_type = SampleType.parse(re_match.group(1))
        self.__size = int(re_match.group(2))
        super().__init__(dbg_value, name, data_type)

    @property
    def size(self) -> int:
        return self.__size

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_from_debugger(self) -> np.ndarray:
        assert isinstance(self._value, AbstractValue)
        array = self._value.readmemory(
            self._value.address(), self.byte_size, self.dtype
        )
        return array.reshape(self.shape())


class StdVector(Container1D):
    __REGEX = rf"^(?:const\s+)?std::vector<{SampleType.regex()},.*>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(f"Could not parse {typename} as a valid std::vector type")

        datatype = SampleType.parse(re_match.group(1))
        super().__init__(dbg_value, name, datatype)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @property
    def size(self) -> int:
        assert isinstance(self._value, AbstractValue)

        # # via size method
        # try:
        #     return int(self._value.call_method("size"))
        # except RuntimeError:
        #     pass

        # via GNU stdlib members
        try:
            diff = int(self._value.attr("_M_impl").attr("_M_finish")) - int(
                self._value.attr("_M_impl").attr("_M_start")
            )
            if diff == 0:
                return 0
            byte_size = self.__data_ptr_value()[0].byte_size()
            return int(diff / byte_size)
        except RuntimeError:
            raise RuntimeError(
                f"Failed to retrieve size of {self._value.typename()}. "
                "Consider disabling optimization or use a supported stdlib version"
            )

    def __data_ptr_value(self) -> AbstractValue:
        assert isinstance(self._value, AbstractValue)

        # # via data method
        # try:
        #     return self._value.call_method("data")
        # except RuntimeError:
        #     pass

        # via GNU stdlib members
        try:
            return self._value.attr("_M_impl").attr("_M_start")
        except RuntimeError:
            raise RuntimeError(
                f"Failed to retrieve data ptr of {self._value.typename()}. "
                "Consider disabling optimization or use a supported stdlib version"
            )

    def read_from_debugger(self) -> np.ndarray:
        assert isinstance(self._value, AbstractValue)
        array = self._value.readmemory(
            int(self.__data_ptr_value()), self.byte_size, self.dtype
        )
        return array.reshape(self.shape())


class StdSpan(Container1D):
    __REGEX = rf"^(?:const\s+)?std::span<{SampleType.regex()},\s*(\d+)>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(f"Could not parse {typename} as a valid std::span type")

        self.__extent = int(re_match.group(2))
        datatype = SampleType.parse(re_match.group(1))
        super().__init__(dbg_value, name, datatype)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @property
    def size(self) -> int:
        assert isinstance(self._value, AbstractValue)
        if self.__extent != 18446744073709551615:
            return self.__extent
        else:
            # # via size method
            # try:
            #     return int(self._value.call_method("size"))
            # except RuntimeError:
            #     pass

            # via GNU stdlib members
            try:
                return int(self._value.attr("_M_extent").attr("_M_extent_value"))
            except:
                raise RuntimeError(
                    f"Failed to retrieve size of {self._value.typename()}. "
                    "Consider disabling optimization or use a supported stdlib version"
                )

    def __data_ptr(self) -> int:
        assert isinstance(self._value, AbstractValue)
        # via data method
        # try:
        #     return int(self._value.call_method("data"))
        # except RuntimeError:
        #     pass

        # via GNU stdlib members
        try:
            return int(self._value.attr("_M_ptr"))
        except RuntimeError:
            raise RuntimeError(
                f"Failed to retrieve data ptr of {self._value.typename()}. "
                "Consider disabling optimizations or use a supported stdlib version"
            )

    def read_from_debugger(self) -> np.ndarray:
        assert isinstance(self._value, AbstractValue)
        array = self._value.readmemory(self.__data_ptr(), self.byte_size, self.dtype)
        return array.reshape(self.shape())


ContainerFactory().register(CArray1D)
ContainerFactory().register(StdArray)
ContainerFactory().register(StdVector)
ContainerFactory().register(StdSpan)
ContainerFactory().register(Pointer1D)
