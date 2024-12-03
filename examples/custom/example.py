from __future__ import annotations

import re
from typing import Callable, List, Tuple

from dave.common.logger import Logger
from dave.server.container import SampleType, Container1D, Container2D
from dave.server.entity_factor import EntityFactory
from dave.server.debuggers.value import AbstractValue
from dave.server.languages import c_cpp


################################################################################
###                             DaveCustomContainerPtr
################################################################################
class DaveCustomContainerPtr(Container1D):
    """
    Custom container support example.This classes represent 1D (mono)
    audio data, using a float*

    template <typename T>
    struct DaveCustomContainerPtr final {
        T* ptr_{};
        int size_{};
    };
    """

    __REGEX = rf"(?:const\s+)?DaveCustomContainerPtr<{SampleType.regex()}>\s*$"

    # Required for 1D container
    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"DaveCustomContainerPtr could not parse {typename} as a valid type"
            )

        data_type = SampleType.parse(re_match.group(1))
        super().__init__(dbg_value, name, data_type)

        # Use the preexisting 1D pointer container type
        self.__inner = c_cpp.Pointer1D(
            dbg_value.attr("ptr_"),
            name + ".ptr_",
            [
                self.size,
            ],
        )

    # Required for all containers
    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    # Required for 1D container
    @property
    def size(self) -> int:
        assert isinstance(self._value, AbstractValue)
        try:
            return int(self._value.attr("size_"))
        except:
            raise RuntimeError(
                f"Failed to retrieve size of {self._value.typename()}. "
                "Consider disabling optimization or use a supported stdlib version"
            )

    # Required for all containers
    def read_from_debugger(self) -> bytearray:
        return self.__inner.read_from_debugger()


# Required for 1D container
DaveCustomContainerPtr.register()


################################################################################
###                           DaveCustomContainerPtrPtr
################################################################################
class DaveCustomContainerPtrPtr(Container2D):
    """
    Custom container support example. This classes represent non-interleaved 2D
    audio data, using a float** to point on each channel

    struct DaveCustomContainerPtrPtr {
        float** ptr_{};
        int block_size_{};
        int channels_{};
    };
    """

    __REGEX = rf"(?:const\s+)?DaveCustomContainerPtrPtr\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"DaveCustomContainerPtrPtr could not parse {typename} as a valid type"
            )

        data_type = SampleType.parse("float")
        super().__init__(dbg_value, name, data_type)

        # Use the preexisting 2D pointer pointer container type
        self.__inner = c_cpp.Pointer2D(
            dbg_value.attr("ptr_"), name + ".ptr_", self.shape()
        )

    # Required for all containers
    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    # Required for 2D containers
    def shape(self) -> Tuple[int, int]:
        assert isinstance(self._value, AbstractValue)
        try:
            return (
                # if interleaved, the order should be inverted
                int(self._value.attr("channels_")),
                int(self._value.attr("block_size_")),
            )
        except:
            raise RuntimeError(
                f"Failed to retrieve shape of {self._value.typename()}. "
                "Consider disabling optimization"
            )

    # Required for all containers
    def read_from_debugger(self) -> bytearray:
        return self.__inner.read_from_debugger()


# Required for all containers
DaveCustomContainerPtrPtr.register()


################################################################################
###                           DaveCustomInterleavedContainerVec
################################################################################
class DaveCustomInterleavedContainerVec(Container2D):
    """
    Custom container support example. This classes represent interleaved 2D
    audio data, using a std::vector to contains all the channels data

    struct DaveCustomInterleavedContainerVec {
        std::vector<float> vec_{};
        int block_size_{};
        int channels_{};
    };
    """

    __REGEX = rf"(?:const\s+)?DaveCustomInterleavedContainerVec\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"DaveCustomInterleavedContainerVec could not parse {typename} as a valid type"
            )

        data_type = SampleType.parse("float")
        super().__init__(dbg_value, name, data_type, interleaved=True)

        # Use the preexisting 1D vector container type
        self.__inner = c_cpp.StdVector1D(dbg_value.attr("vec_"), name + ".vec_")

    # Required for all containers
    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    # Required for 2D containers
    def shape(self) -> Tuple[int, int]:
        assert isinstance(self._value, AbstractValue)
        try:
            return (
                # Interleaved
                int(self._value.attr("block_size_")),
                int(self._value.attr("channels_")),
            )
        except:
            raise RuntimeError(
                f"Failed to retrieve shape of {self._value.typename()}. "
                "Consider disabling optimization"
            )

    # Required for all containers
    def read_from_debugger(self) -> bytearray:
        return self.__inner.read_from_debugger()


# Required for all containers
DaveCustomInterleavedContainerVec.register()


################################################################################
###                           DaveCustomContainerVecRef
################################################################################
class DaveCustomContainerVecRef(Container2D):
    """
    Custom container support example. This classes represent planar 1D
    audio data, using a std::vector reference

    struct DaveCustomContainerVecRef {
        std::vector<float>& vec_ref_;
        int block_size_{};
    };
    """

    __REGEX = rf"(?:const\s+)?DaveCustomContainerVecRef\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"DaveCustomInterleavedContainerVec could not parse {typename} as a valid type"
            )

        data_type = SampleType.parse("float")
        super().__init__(dbg_value, name, data_type)

        # Use the preexisting 1D vector container type
        self.__inner = c_cpp.StdVector1D(
            dbg_value.attr("vec_ref_"),
            name + ".vec_ref_",
        )

    # Required for all containers
    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    # Required for 2D containers
    def shape(self) -> Tuple[int, int]:
        assert isinstance(self._value, AbstractValue)
        try:
            return (
                # if interleaved, the order should be inverted
                int(self._value.attr("channels_")),
                int(self._value.attr("block_size_")),
            )
        except:
            raise RuntimeError(
                f"Failed to retrieve shape of {self._value.typename()}. "
                "Consider disabling optimization"
            )

    # Required for all containers
    def read_from_debugger(self) -> bytearray:
        return self.__inner.read_from_debugger()


# Required for all containers
DaveCustomContainerVecRef.register()
