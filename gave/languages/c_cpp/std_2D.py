# from abc import ABC, abstractmethod
# from enum import Enum
import re
from typing import List, Tuple

# import gdb  # type: ignore
# import gdb.types  # type: ignore
import numpy as np

from gave.container import SampleType, Container2D
from gave.container_factory import ContainerFactory
from gave.debuggers.value import AbstractValue


class CArrayAny2D(Container2D):
    """
    Match any C table of containers, except for 2D C table. These should match
    CarrayC2D
    """

    __REGEX = rf"^(?:const\s+)?([^[\]]*)\s*\[(\d+)\]$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(f"Could not parse {typename} as a valid C array type")

        # Check if contains a nested valid 1D container
        nested = re_match.group(1)
        if not ContainerFactory().check_valid_1D(nested):
            raise TypeError(
                f"Could not parse nested type {nested} as a valid container type"
            )

        self.__size = int(re_match.group(2))
        self.__nested_containers = [
            ContainerFactory().build_1D(
                dbg_value[i],
                dbg_value[i].typename(),
                "",
                _,
            )
            for i in range(self.__size)
        ]
        super().__init__(dbg_value, name, self.__nested_containers[0].float_type)

    def shape(self) -> Tuple[int, int]:
        return (self.__size, self.__nested_containers[0].size)

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_from_debugger(self) -> np.ndarray:
        ret = np.ndarray(self.shape())
        for i in range(self.__size):
            ret[i][:] = self.__nested_containers[i].read_from_debugger()
        return ret


class CarrayCarray2D(Container2D):
    """
    Match 2D C table of float values
    """

    __REGEX = rf"^(?:const\s+)?{SampleType.regex()}\s*\[(\d+)\]\s*\[(\d+)\]$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(f"Could not parse {typename} as a valid 2D C array type")

        # Check if contains a nested valid 1D container
        data_type = SampleType.parse(re_match.group(1))
        self.__shape = (int(re_match.group(2)), int(re_match.group(3)))
        super().__init__(dbg_value, name, data_type)

    def shape(self) -> Tuple[int, int]:
        return self.__shape

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @property
    def byte_size(self) -> int:
        return self.float_type.byte_size() * self.shape()[0] * self.shape()[1]

    def read_from_debugger(self) -> np.ndarray:
        assert isinstance(self._value, AbstractValue)
        array = self._value.readmemory(
            self._value.address(), self.byte_size, dtype=self.dtype
        )
        return array.reshape(self.shape())


class Pointer2D(Container2D):
    """
    Match any ptr of containers
    """

    __REGEX = rf"^(?:const\s+)?(.*)\s*\*$"

    def __init__(self, dbg_value: AbstractValue, name: str, dims: List[int]):
        typename = dbg_value.typename()
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(f"Could not parse {typename} as a valid ptr ptr type")

        # Check if contains a nested valid 1D container
        nested = re_match.group(1)
        if not ContainerFactory().check_valid_1D(nested):
            raise TypeError(
                f"Could not parse nested type {nested} as a valid container type"
            )

        if "*" in nested and len(dims) != 2:
            raise TypeError(
                "Pointer of pointer container requires exactly two dimensions"
            )
        elif not "*" in nested and len(dims) != 1:
            raise TypeError("Pointer container requires exactly one dimensions")

        self.__size = dims[0]
        self.__nested_containers = [
            ContainerFactory().build_1D(
                dbg_value[i],
                dbg_value[i].typename(),
                "",
                dims[1:],
            )
            for i in range(self.__size)
        ]
        super().__init__(dbg_value, name, self.__nested_containers[0].float_type)

    def shape(self) -> Tuple[int, int]:
        return (self.__size, self.__nested_containers[0].size)

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_from_debugger(self) -> np.ndarray:
        ret = np.ndarray(self.shape())
        for i in range(self.__size):
            ret[i][:] = self.__nested_containers[i].read_from_debugger()
        return ret


class StdArray2D(Container2D):
    __REGEX = rf"^(?:const\s+)?std::array<(.*),\s*(\d+)>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(f"Could not parse {typename} as a valid std::array type")

        # Check if contains a nested valid 1D container
        nested = re_match.group(1)
        if not ContainerFactory().check_valid_1D(nested):
            raise TypeError(
                f"Could not parse nested type {nested} as a valid container type"
            )

        self.__size = int(re_match.group(2))
        self._value = dbg_value
        self.__nested_containers = [
            ContainerFactory().build_1D(
                self.__data_ptr_value()[i],
                self.__data_ptr_value()[i].typename(),
                "",
                _,
            )
            for i in range(self.__size)
        ]
        super().__init__(dbg_value, name, self.__nested_containers[0].float_type)

    def shape(self) -> Tuple[int, int]:
        return (self.__size, self.__nested_containers[0].size)

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def __data_ptr_value(self) -> AbstractValue:
        assert isinstance(self._value, AbstractValue)

        # # via data method
        # try:
        #     return self._value.call_method("data")
        # except RuntimeError:
        #     pass

        # via GNU stdlib members
        try:
            return self._value.attr("_M_elems")
        except RuntimeError:
            raise RuntimeError(
                f"Failed to retrieve data ptr of {self._value.typename()}. "
                "Consider disabling optimization or use a supported stdlib version"
            )

    def read_from_debugger(self) -> np.ndarray:
        ret = np.ndarray(self.shape())
        for i in range(self.__size):
            ret[i][:] = self.__nested_containers[i].read_from_debugger()
        return ret


class StdVector2D(Container2D):
    __REGEX = rf"^(?:const\s+)?std::vector<(.*),.*>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(f"Could not parse {typename} as a valid std::array type")

        # Check if contains a nested valid 1D container
        nested = re_match.group(1)
        if not ContainerFactory().check_valid_1D(nested):
            raise TypeError(
                f"Could not parse nested type {nested} as a valid container type"
            )

        self._value = dbg_value
        self.__nested_containers = [
            ContainerFactory().build_1D(
                self.__data_ptr_value()[i],
                self.__data_ptr_value()[i].typename(),
                "",
                _,
            )
            for i in range(self.size)
        ]
        super().__init__(dbg_value, name, self.__nested_containers[0].float_type)

    @property
    def size(self) -> int:
        assert isinstance(self._value, AbstractValue)

        # # via size method
        # try:
        #     size = self._value.call_method("size")
        #     if not size.IsValid() or size.value is None:
        #         raise RuntimeError
        #     return int(size)
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

    def shape(self) -> Tuple[int, int]:
        return (self.size, self.__nested_containers[0].size)

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_from_debugger(self) -> np.ndarray:
        ret = np.ndarray(self.shape())
        for i in range(self.size):
            ret[i][:] = self.__nested_containers[i].read_from_debugger()
        return ret


class StdSpan2D(Container2D):
    __REGEX = rf"^(?:const\s+)?std::span<(.*),\s*(\d+)>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(f"Could not parse {typename} as a valid std::array type")

        # Check if contains a nested valid 1D container
        nested = re_match.group(1)
        if not ContainerFactory().check_valid_1D(nested):
            raise TypeError(
                f"Could not parse nested type {nested} as a valid container type"
            )

        self.__extent = int(re_match.group(2))
        self._value = dbg_value
        self.__nested_containers = [
            ContainerFactory().build_1D(
                StdSpan2D.__data_ptr_value(dbg_value)[i],
                StdSpan2D.__data_ptr_value(dbg_value)[i].typename(),
                "",
                _,
            )
            for i in range(self.size)
        ]
        super().__init__(dbg_value, name, self.__nested_containers[0].float_type)

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

    @staticmethod
    def __data_ptr_value(value: AbstractValue) -> AbstractValue:
        # # via data method
        # try:
        #     return value.call_method("data")
        # except RuntimeError:
        #     pass

        # via GNU stdlib members
        try:
            return value.attr("_M_ptr")
        except RuntimeError:
            raise RuntimeError(
                f"Failed to retrieve data ptr of {value.typename()}. "
                "Consider disabling optimizations or use a supported stdlib version"
            )

    def shape(self) -> Tuple[int, int]:
        return (self.size, self.__nested_containers[0].size)

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_from_debugger(self) -> np.ndarray:
        ret = np.ndarray(self.shape())
        for i in range(self.size):
            ret[i][:] = self.__nested_containers[i].read_from_debugger()
        return ret


ContainerFactory().register(CArrayAny2D)
ContainerFactory().register(CarrayCarray2D)
ContainerFactory().register(Pointer2D)
ContainerFactory().register(StdArray2D)
ContainerFactory().register(StdVector2D)
ContainerFactory().register(StdSpan2D)
