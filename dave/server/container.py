from __future__ import annotations
from abc import ABC, abstractmethod
import re
from typing import Any, Callable, List, Tuple, Type, Union
import struct
import cmath

# from dave.common.data_layout import RawContainer.Layout
from dave.common.sample_type import SampleType
from dave.common.raw_container import RawContainer

from .debuggers.value import AbstractValue
from .entity import Entity


class Container(Entity):
    """
    The base class for every audio container class dave can support.

    When implementing support for a new type of container, you need to derive from
    either Container1D or Container2D
    """

    def __init__(
        self, dbg_value: Any, name: str, data_type: SampleType, interleaved: bool
    ) -> None:
        super().__init__(dbg_value, name)
        self.__interleaved = interleaved
        self.__type = data_type

    def compute_summary(self) -> str:
        shape = self.shape()
        channels, samples = shape if not self.__interleaved else shape[::-1]

        samples_bytes = self.read_from_debugger()
        byte_size = self.float_type.byte_size()
        fmt = self.float_type.struct_name()

        if self.float_type.is_complex():
            return f"{channels} channels {samples} samples (complex data)"
        else:
            min_amp = struct.unpack(fmt, samples_bytes[:byte_size])[0]
            max_amp = min_amp
            for i in range(1, channels * samples):
                sample_bytes = samples_bytes[i * byte_size : (i + 1) * byte_size]
                sample = struct.unpack(fmt, sample_bytes)[0]
                min_amp = min(min_amp, sample)
                max_amp = max(max_amp, sample)
            return f"{channels} channels {samples} samples, min {min_amp:.4E}, max {max_amp:.4E}"

    def compute_sparklines(self) -> List[str]:
        assert not self.float_type.is_complex()
        shape = self.shape()
        channels, num_samples = shape if not self.__interleaved else shape[::-1]
        samples_bytes = self.read_from_debugger()
        byte_size = self.float_type.byte_size()
        fmt = self.float_type.struct_name()

        sparklines = []

        for channel in range(channels):
            if self.__interleaved:
                channel_samples = [
                    struct.unpack(
                        fmt,
                        samples_bytes[
                            (num_samples * i + channel)
                            * byte_size : (num_samples * i + channel + 1)
                            * byte_size
                        ],
                    )[0]
                    for i in range(num_samples)
                ]
            else:
                channel_samples = [
                    struct.unpack(
                        fmt,
                        samples_bytes[
                            (num_samples * channel + i)
                            * byte_size : (num_samples * channel + i + 1)
                            * byte_size
                        ],
                    )[0]
                    for i in range(num_samples)
                ]

            waveform = "_⎽⎼—⎻⎺‾"
            maxValue = max(channel_samples)
            if maxValue > 0.0:
                scale = maxValue
            else:
                scale = 1.0
            num_zeros = 0
            output = "["

            for i in range(len(channel_samples)):
                sample = channel_samples[i]
                if sample == 0.0:
                    if num_zeros == 0:
                        output += "0"
                    num_zeros += 1
                    continue
                else:
                    num_zeros = 0

                if num_zeros > 1:
                    output += "(" + str(num_zeros) + ")"
                    num_zeros = 0
                # for some reason sys.float_info.epsilon is nowhere near
                # the rounding error introduced by lldb when importing float values to python
                if (abs(sample) - 0.00000015) > 1.0:  # out of bounds?
                    output += "E"
                elif sample == float("+inf") or sample == float("-inf"):
                    output += "I"
                elif sample == float("nan"):
                    output += "N"
                elif (i > 0) and ((sample < 0) is not (channel_samples[i - 1] < 0)):
                    output += "x"  # zero crossing
                else:
                    # normalize so we can see detail
                    sample /= scale
                    # make it a positive number that varies from 0 to 6
                    index = int((sample + 1) / 2.0 * 6.99)
                    character = waveform[index]
                    if output[-1] != character:
                        output += character

            if num_zeros > 1:
                output += "(" + str(num_zeros) + ")"

            output += "]"
            sparklines.append(output)
        return sparklines

    def as_raw(self) -> RawContainer:
        return RawContainer(
            # base
            self.id,
            self.name,
            self.default_layout(),
            self.available_data_layouts(),
            # container
            self.read_from_debugger(),
            self.shape(),
            self.dimensions_fixed(),
            self.__interleaved,
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
    def available_data_layouts(cls) -> List[RawContainer.Layout]:
        pass

    @staticmethod
    @abstractmethod
    def dimensions_fixed() -> bool:
        """
        Should return true if the container class already indicates the number of
        channels as part of its design
        """
        pass

    @abstractmethod
    def default_layout() -> RawContainer.Layout:
        pass

    @abstractmethod
    def read_from_debugger(self) -> bytearray:
        pass

    @staticmethod
    def formatter_compatible():
        return True

    @staticmethod
    def supports_concat() -> bool:
        return RawContainer.supports_concat()


class Container1D(Container):
    def __init__(self, dbg_value: Any, name: str, data_type: SampleType) -> None:
        super().__init__(dbg_value, name, data_type, False)

    @property
    @abstractmethod
    def size(self) -> int:
        pass

    def shape(self) -> Tuple[int, int]:
        return (1, self.size)

    def default_layout(self) -> RawContainer.Layout:
        if self.float_type.is_complex():
            return RawContainer.Layout.CPX_1D
        else:
            return RawContainer.Layout.REAL_1D

    @classmethod
    def available_data_layouts(cls) -> List[RawContainer.Layout]:
        if not cls.dimensions_fixed():
            return [
                RawContainer.Layout.CPX_1D,
                RawContainer.Layout.CPX_2D,
                RawContainer.Layout.REAL_1D,
                RawContainer.Layout.REAL_2D,
            ]
        else:
            return [
                RawContainer.Layout.CPX_1D,
                RawContainer.Layout.REAL_1D,
            ]

    @staticmethod
    def dimensions_fixed() -> bool:
        return False

    @staticmethod
    def is_nested() -> bool:
        return False


class Container2D(Container):
    def __init__(
        self,
        dbg_value: Any,
        name: str,
        data_type: SampleType,
        interleaved: bool = False,
    ) -> None:
        super().__init__(dbg_value, name, data_type, interleaved)

    def default_layout(self) -> RawContainer.Layout:
        if self.float_type.is_complex():
            return RawContainer.Layout.CPX_2D
        else:
            return RawContainer.Layout.REAL_2D

    @classmethod
    def available_data_layouts(cls) -> List[RawContainer.Layout]:
        return [
            RawContainer.Layout.CPX_2D,
            RawContainer.Layout.REAL_2D,
        ]

    @staticmethod
    def dimensions_fixed() -> bool:
        return True

    @staticmethod
    def is_nested() -> bool:
        return False
