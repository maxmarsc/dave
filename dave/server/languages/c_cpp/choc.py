from __future__ import annotations

import re
from typing import Callable, List, Tuple


from dave.common.logger import Logger
from ...container import SampleType, Container2D, Container1D
from ...debuggers.value import AbstractValue


class ChocMonoView(Container1D):
    __REGEX = rf"^(?:const\s+)?choc::buffer::BufferView<{SampleType.regex()},\s?choc::buffer::MonoLayout>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        typename = dbg_value.typename()
        sample_type, _ = self.parse_typename(typename)
        super().__init__(dbg_value, name, sample_type)

    @property
    def size(self) -> int:
        assert isinstance(self._value, AbstractValue)

        return int(self._value.attr("size").attr("numFrames"))

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @classmethod
    def parse_typename(cls, typename: str) -> Tuple[SampleType, None]:
        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(f"ChocMonoView could not parse {typename} as a valid type")

        return (SampleType.parse(re_match.group(1)), None)

    def __data_ptr(self) -> int:
        assert isinstance(self._value, AbstractValue)

        return int(self._value.attr("data").attr("data"))

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
        sample_type, _ = self.parse_typename(typename)
        super().__init__(dbg_value, name, sample_type)

        self.__view = ChocMonoView(dbg_value.attr("view"), name=name + ".view")

    @property
    def size(self) -> int:
        return self.__view.size

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @classmethod
    def parse_typename(cls, typename: str) -> Tuple[SampleType, None]:
        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(f"ChocMonoView could not parse {typename} as a valid type")

        return (SampleType.parse(re_match.group(1)), None)

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
        sample_type, *_ = self._parse_typename(typename)
        self._value = dbg_value
        super().__init__(dbg_value, name, sample_type)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @classmethod
    def _parse_typename(cls, typename: str, **_) -> Tuple[SampleType, None, None]:
        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {typename} as a valid choc::buffer::BufferView type"
            )

        return (SampleType.parse(re_match.group(1)), None, None)

    def __channel_data_ptr(self, channel: int) -> int:
        assert isinstance(self._value, AbstractValue)

        offset = int(self._value.attr("data").attr("offset"))
        ptr = int(self._value.attr("data").attr("channels")[channel])
        return ptr + self.sample_type.byte_size() * offset

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
                    self.sample_type.byte_size() * self.block_size,
                )
                for channel in range(self.num_channels)
            ]
        )


class ChocChannelArrayBuffer(Container2D):
    __REGEX = rf"^(?:const\s+)?choc::buffer::AllocatedBuffer<{SampleType.regex()},\s?choc::buffer::SeparateChannelLayout>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        typename = dbg_value.typename()
        sample_type, *_ = self._parse_typename(typename)
        self._value = dbg_value
        super().__init__(dbg_value, name, sample_type)

        self.__view = ChocChannelArrayView(dbg_value.attr("view"), name + ".view")

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @classmethod
    def _parse_typename(cls, typename: str, **_) -> Tuple[SampleType, None, None]:
        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {typename} as a valid choc::buffer::AllocatedBuffer type"
            )

        return (SampleType.parse(re_match.group(1)), None, None)

    def shape(self) -> Tuple[int, int]:
        return self.__view.shape()

    def read_from_debugger(self) -> bytearray:
        return self.__view.read_from_debugger()


class ChocInterleavedView(Container2D):
    __REGEX = rf"^(?:const\s+)?choc::buffer::BufferView<{SampleType.regex()},\s?choc::buffer::InterleavedLayout>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        typename = dbg_value.typename()
        sample_type, *_ = self._parse_typename(typename)
        self._value = dbg_value
        super().__init__(dbg_value, name, sample_type, interleaved=True)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @classmethod
    def _parse_typename(cls, typename: str, **_) -> Tuple[SampleType, None, None]:
        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {typename} as a valid choc::buffer::BufferView type"
            )

        return (SampleType.parse(re_match.group(1)), None, None)

    def __data_ptr(self) -> int:
        assert isinstance(self._value, AbstractValue)

        return int(self._value.attr("data").attr("data"))

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
        sample_type, *_ = self._parse_typename(typename)
        self._value = dbg_value
        super().__init__(dbg_value, name, sample_type, interleaved=True)

        self.__view = ChocInterleavedView(dbg_value.attr("view"), name + ".view")

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @classmethod
    def _parse_typename(cls, typename: str, **_) -> Tuple[SampleType, None, None]:
        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {typename} as a valid choc::buffer::AllocatedBuffer type"
            )

        return (SampleType.parse(re_match.group(1)), None, None)

    def shape(self) -> Tuple[int, int]:
        return self.__view.shape()

    def read_from_debugger(self) -> bytearray:
        return self.__view.read_from_debugger()


ChocMonoView.register()
ChocMonoBuffer.register()
ChocChannelArrayView.register()
ChocChannelArrayBuffer.register()
ChocInterleavedView.register()
ChocInterleavedBuffer.register()
