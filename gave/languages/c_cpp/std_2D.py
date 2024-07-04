from abc import ABC, abstractmethod
from enum import Enum
import re
from typing import List, Tuple
import gdb  # type: ignore
import gdb.types  # type: ignore
import numpy as np

from gave.container import SampleType, Container2D
from gave.container_factory import ContainerFactory


class CArrayAny2D(Container2D):
    """
    Match any C table of containers, except for 2D C table. These should match
    CarrayC2D
    """

    __REGEX = rf"^(?:const\s+)?([^[\]]*)\s*\[(\d+)\]$"

    def __init__(self, gdb_value: gdb.Value, name: str, _):
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(f"Could not parse {gdb_value.type} as a valid C array type")

        # Check if contains a nested valid 1D container
        nested = re_match.group(1)
        if not ContainerFactory().check_valid_1D(nested):
            raise TypeError(
                f"Could not parse nested type {nested} as a valid container type"
            )

        self.__size = int(re_match.group(2))
        self.__nested_containers = [
            ContainerFactory().build_1D(
                gdb_value[i], str(gdb.types.get_basic_type(gdb_value[i].type)), "", _
            )
            for i in range(self.__size)
        ]
        super().__init__(gdb_value, name, self.__nested_containers[0].float_type)

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

    def __init__(self, gdb_value: gdb.Value, name: str, _):
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {gdb_value.type} as a valid 2D C array type"
            )

        # Check if contains a nested valid 1D container
        data_type = SampleType.parse(re_match.group(1))
        self.__shape = (int(re_match.group(2)), int(re_match.group(3)))
        super().__init__(gdb_value, name, data_type)

    def shape(self) -> Tuple[int, int]:
        return self.__shape

    @classmethod
    def regex_name(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @property
    def byte_size(self) -> int:
        return self.float_type.byte_size() * self.shape()[0] * self.shape()[1]

    def read_from_debugger(self) -> np.ndarray:
        assert isinstance(self._value, gdb.Value)
        inferior = gdb.selected_inferior()
        array = np.frombuffer(
            inferior.read_memory(self._value[0].address, self.byte_size),
            dtype=self.dtype,
        )
        return array.reshape(self.shape())


class Pointer2D(Container2D):
    """
    Match any ptr of containers
    """

    __REGEX = rf"^(?:const\s+)?(.*)\s*\*$"

    def __init__(self, gdb_value: gdb.Value, name: str, dims: List[int]):
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(f"Could not parse {gdb_value.type} as a valid ptr ptr type")

        # Check if contains a nested valid 1D container
        nested = re_match.group(1)
        if not ContainerFactory().check_valid_1D(nested):
            raise TypeError(
                f"Could not parse nested type {nested} as a valid container type"
            )

        if "*" in nested and len(dims) != 2:
            raise gdb.GdbError(
                "Pointer of pointer container requires exactly two dimensions"
            )
        elif not "*" in nested and len(dims) != 1:
            raise gdb.GdbError("Pointer container requires exactly one dimensions")

        self.__size = dims[0]
        self.__nested_containers = [
            ContainerFactory().build_1D(
                gdb_value[i],
                str(gdb.types.get_basic_type(gdb_value[i].type)),
                "",
                dims[1:],
            )
            for i in range(self.__size)
        ]
        super().__init__(gdb_value, name, self.__nested_containers[0].float_type)

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

    def __init__(self, gdb_value: gdb.Value, name: str, _):
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {gdb_value.type} as a valid std::array type"
            )

        # Check if contains a nested valid 1D container
        nested = re_match.group(1)
        if not ContainerFactory().check_valid_1D(nested):
            raise TypeError(
                f"Could not parse nested type {nested} as a valid container type"
            )

        self.__size = int(re_match.group(2))
        self.__nested_containers = [
            ContainerFactory().build_1D(
                gdb_value["_M_elems"][i],
                str(gdb.types.get_basic_type(gdb_value["_M_elems"][i].type)),
                "",
                _,
            )
            for i in range(self.__size)
        ]
        super().__init__(gdb_value, name, self.__nested_containers[0].float_type)

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


class StdVector2D(Container2D):
    __REGEX = rf"^(?:const\s+)?std::vector<(.*),\s*.*<\1\s?>\s*>\s*$"

    def __init__(self, gdb_value: gdb.Value, name: str, _):
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {gdb_value.type} as a valid std::array type"
            )

        # Check if contains a nested valid 1D container
        nested = re_match.group(1)
        if not ContainerFactory().check_valid_1D(nested):
            raise TypeError(
                f"Could not parse nested type {nested} as a valid container type"
            )

        self._value = gdb_value
        self.__nested_containers = [
            ContainerFactory().build_1D(
                gdb_value["_M_impl"]["_M_start"][i],
                str(gdb.types.get_basic_type(gdb_value["_M_impl"]["_M_start"][i].type)),
                "",
                _,
            )
            for i in range(self.size)
        ]
        super().__init__(gdb_value, name, self.__nested_containers[0].float_type)

    @property
    def size(self) -> int:
        return int(
            self._value["_M_impl"]["_M_finish"] - self._value["_M_impl"]["_M_start"]
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

    def __init__(self, gdb_value: gdb.Value, name: str, _):
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        re_match = self.regex_name().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {gdb_value.type} as a valid std::array type"
            )

        # Check if contains a nested valid 1D container
        nested = re_match.group(1)
        if not ContainerFactory().check_valid_1D(nested):
            raise TypeError(
                f"Could not parse nested type {nested} as a valid container type"
            )

        self.__extent = int(re_match.group(2))
        self._value = gdb_value
        self.__nested_containers = [
            ContainerFactory().build_1D(
                gdb_value["_M_ptr"][i],
                str(gdb.types.get_basic_type(gdb_value["_M_ptr"][i].type)),
                "",
                _,
            )
            for i in range(self.size)
        ]
        print("built")
        super().__init__(gdb_value, name, self.__nested_containers[0].float_type)

    @property
    def size(self) -> int:
        if self.__extent != 18446744073709551615:
            return self.__extent
        else:
            return int(self._value["_M_extent"]["_M_extent_value"])

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
