from __future__ import annotations

import re
from typing import Tuple

from ...container import SampleType, Container2D
from ...debuggers.value import AbstractValue, DebuggerMemoryError

class HartAudioBuffer(Container2D):
    __REGEX = rf"^(?:const\s+)?hart::AudioBuffer<{SampleType.regex()}>\s*$"

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
            raise TypeError(f"Could not parse {typename} as a valid hart::AudioBuffer type")
        return (SampleType.parse(re_match.group(1)), None, None)

    @property
    def num_channels(self) -> int:
        return int(self._value.attr("m_numChannels"))

    @property
    def block_size(self) -> int:
        return int(self._value.attr("m_numFrames"))

    def shape(self) -> Tuple[int, int]:
        return (self.num_channels, self.block_size)

    def __channel_data_ptr(self, channel: int) -> int:
        wrapped_vec = self._value.attr("m_channelPointers")
        raw_vec = wrapped_vec._GdbValue__value
        start = raw_vec["_M_impl"]["_M_start"]
        return int(start[channel])

    def read_from_debugger(self) -> bytearray:
        if self.num_channels <= 0:
            raise DebuggerMemoryError("m_numChannels is <= 0")
        return b"".join(
            self._value.readmemory(
                self.__channel_data_ptr(channel),
                self.sample_type.byte_size() * self.block_size,
            )
            for channel in range(self.num_channels)
        )

HartAudioBuffer.register()
