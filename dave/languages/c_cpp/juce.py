from __future__ import annotations

import re
from typing import Callable, List, Tuple

import numpy as np

from ...container import SampleType, Container2D
from ...container_factory import ContainerFactory
from ...debuggers.value import AbstractValue
from ...logger import Logger


class JuceAudioBuffer(Container2D):
    __REGEX = rf"^(?:const\s+)?juce::AudioBuffer<{SampleType.regex()}>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {typename} as a valid juce::AudioBuffer type"
            )

        self._value = dbg_value
        datatype = SampleType.parse(re_match.group(1))
        super().__init__(dbg_value, name, datatype)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @property
    def num_channels(self) -> int:
        return int(self._value.attr("numChannels"))

    @property
    def block_size(self) -> int:
        return int(self._value.attr("size"))

    @property
    def shape(self) -> Tuple[int, int]:
        return (self.num_channels, self.block_size)

    def __channel_data_ptr(self, channel: int) -> int:
        return int(self._value.attr("channels")[channel])

    def read_from_debugger(self) -> np.ndarray:
        assert isinstance(self._value, AbstractValue)
        array = np.ndarray(self.shape, dtype=self.dtype)
        for channel in range(self.num_channels):
            array[channel, :] = self._value.readmemory(
                self.__channel_data_ptr(channel),
                self.float_type.byte_size() * self.block_size,
                self.dtype,
            )
        return array


class JuceAudioBlock(Container2D):
    __REGEX = rf"^(?:const\s+)?juce::dsp::AudioBlock<{SampleType.regex()}>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {typename} as a valid juce::dsp::AudioBlock type"
            )

        self._value = dbg_value
        datatype = SampleType.parse(re_match.group(1))
        super().__init__(dbg_value, name, datatype)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @property
    def num_channels(self) -> int:
        return int(self._value.attr("numChannels"))

    @property
    def block_size(self) -> int:
        return int(self._value.attr("numSamples"))

    @property
    def shape(self) -> Tuple[int, int]:
        return (self.num_channels, self.block_size)

    def __channel_data_ptr(self, channel: int) -> int:
        start = int(self._value.attr("startSample"))
        return self._value.attr("channels")[channel][start].address()

    def read_from_debugger(self) -> np.ndarray:
        assert isinstance(self._value, AbstractValue)
        array = np.ndarray(self.shape, dtype=self.dtype)
        for channel in range(self.num_channels):
            array[channel, :] = self._value.readmemory(
                self.__channel_data_ptr(channel),
                self.float_type.byte_size() * self.block_size,
                self.dtype,
            )
        return array


ContainerFactory().register(JuceAudioBuffer)
ContainerFactory().register(JuceAudioBlock)
