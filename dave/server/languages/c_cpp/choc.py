from __future__ import annotations

import re
from typing import Callable, List, Tuple


from dave.common.logger import Logger
from ...container import SampleType, Container2D, Container1D
from ...container_factory import ContainerFactory
from ...debuggers.value import AbstractValue


class ChocMonoView(Container1D):
    __REGEX = rf"^(?:const\s+)?choc::buffer::BufferView<{SampleType.regex()},\s?choc::buffer::MonoLayout>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(f"ChocMonoView could not parse {typename} as a valid type")

        data_type = SampleType.parse(re_match.group(1))
        super().__init__(dbg_value, name, data_type)

    @property
    def size(self) -> int:
        assert isinstance(self._value, AbstractValue)

        try:
            return int(self._value.attr("size").attr("numFrames"))
        except:
            raise RuntimeError(
                f"Failed to retrieve size of {self._value.typename()}. "
                "Consider disabling optimization or use a supported version"
            )

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def __data_ptr(self) -> int:
        assert isinstance(self._value, AbstractValue)

        try:
            return int(self._value.attr("data").attr("data"))
        except:
            raise RuntimeError(
                f"Failed to retrieve size of {self._value.typename()}. "
                "Consider disabling optimization or use a supported version"
            )

    def read_from_debugger(self) -> bytearray:
        assert isinstance(self._value, AbstractValue)
        return self._value.readmemory(self.__data_ptr(), self.byte_size)

    @staticmethod
    def dimensions_fixed() -> bool:
        # This class cannot be used to represent multichannel audio
        return True


class ChocMonoBuffer(Container1D):
    __REGEX = rf"^(?:const\s+)?choc::buffer::AllocatedBuffer<{SampleType.regex()},\s?choc::buffer::MonoLayout>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(f"ChocMonoView could not parse {typename} as a valid type")

        data_type = SampleType.parse(re_match.group(1))
        super().__init__(dbg_value, name, data_type)

        self.__view = ChocMonoView(dbg_value.attr("view"), name=name + ".view")

    @property
    def size(self) -> int:
        return self.__view.size

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_from_debugger(self) -> bytearray:
        return self.__view.read_from_debugger()

    @staticmethod
    def dimensions_fixed() -> bool:
        # This class cannot be used to represent multichannel audio
        return True


class ChocChannelArrayView(Container2D):
    __REGEX = rf"^(?:const\s+)?choc::buffer::BufferView<{SampleType.regex()},\s?choc::buffer::SeparateChannelLayout>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"ChocChannelArrayView could not parse {typename} as a valid type"
            )

        data_type = SampleType.parse(re_match.group(1))
        super().__init__(dbg_value, name, data_type)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def __channel_data_ptr(self, channel: int) -> int:
        assert isinstance(self._value, AbstractValue)

        try:
            offset = int(self._value.attr("data").attr("offset"))
            ptr = int(self._value.attr("data").attr("channels")[channel])
            return ptr + self.float_type.byte_size() * offset
        except:
            raise RuntimeError(
                f"Failed to retrieve size of {self._value.typename()}. "
                "Consider disabling optimization or use a supported version"
            )

    @property
    def num_channels(self) -> int:
        assert isinstance(self._value, AbstractValue)
        return int(self._value.attr("size").attr("numChannels"))

    @property
    def block_size(self) -> int:
        assert isinstance(self._value, AbstractValue)
        return int(self._value.attr("size").attr("numFrames"))

    def shape(self) -> Tuple[int, int]:
        return (self.num_channels, self.block_size)

    def read_from_debugger(self) -> bytearray:
        assert isinstance(self._value, AbstractValue)
        return b"".join(
            [
                self._value.readmemory(
                    self.__channel_data_ptr(channel),
                    self.float_type.byte_size() * self.block_size,
                )
                for channel in range(self.num_channels)
            ]
        )


class ChocChannelArrayBuffer(Container2D):
    __REGEX = rf"^(?:const\s+)?choc::buffer::AllocatedBuffer<{SampleType.regex()},\s?choc::buffer::SeparateChannelLayout>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"ChocChannelArrayView could not parse {typename} as a valid type"
            )

        data_type = SampleType.parse(re_match.group(1))
        super().__init__(dbg_value, name, data_type)

        self.__view = ChocChannelArrayView(dbg_value.attr("view"), name + ".view")

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def shape(self) -> Tuple[int, int]:
        return self.__view.shape()

    def read_from_debugger(self) -> bytearray:
        return self.__view.read_from_debugger()


class ChocInterleavedView(Container2D):
    __REGEX = rf"^(?:const\s+)?choc::buffer::BufferView<{SampleType.regex()},\s?choc::buffer::InterleavedLayout>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"ChocChannelArrayView could not parse {typename} as a valid type"
            )

        data_type = SampleType.parse(re_match.group(1))
        super().__init__(dbg_value, name, data_type, interleaved=True)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def __data_ptr(self) -> int:
        assert isinstance(self._value, AbstractValue)

        try:
            return int(self._value.attr("data").attr("data"))
        except:
            raise RuntimeError(
                f"Failed to retrieve size of {self._value.typename()}. "
                "Consider disabling optimization or use a supported version"
            )

    @property
    def num_channels(self) -> int:
        assert isinstance(self._value, AbstractValue)
        return int(self._value.attr("size").attr("numChannels"))

    @property
    def block_size(self) -> int:
        assert isinstance(self._value, AbstractValue)
        return int(self._value.attr("size").attr("numFrames"))

    def shape(self) -> Tuple[int, int]:
        return (self.block_size, self.num_channels)

    def read_from_debugger(self) -> bytearray:
        assert isinstance(self._value, AbstractValue)
        return self._value.readmemory(self.__data_ptr(), self.byte_size)


class ChocInterleavedBuffer(Container2D):
    __REGEX = rf"^(?:const\s+)?choc::buffer::AllocatedBuffer<{SampleType.regex()},\s?choc::buffer::InterleavedLayout>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"ChocChannelArrayView could not parse {typename} as a valid type"
            )

        data_type = SampleType.parse(re_match.group(1))
        super().__init__(dbg_value, name, data_type, interleaved=True)

        self.__view = ChocInterleavedView(dbg_value.attr("view"), name + ".view")

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def shape(self) -> Tuple[int, int]:
        return self.__view.shape()

    def read_from_debugger(self) -> bytearray:
        return self.__view.read_from_debugger()


ContainerFactory().register(ChocMonoView)
ContainerFactory().register(ChocMonoBuffer)
ContainerFactory().register(ChocChannelArrayView)
ContainerFactory().register(ChocChannelArrayBuffer)
ContainerFactory().register(ChocInterleavedView)
ContainerFactory().register(ChocInterleavedBuffer)
