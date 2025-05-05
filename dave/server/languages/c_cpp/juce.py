from __future__ import annotations

import re
import struct
from typing import Callable, List, Tuple


from dave.common.logger import Logger
from dave.common.raw_iir import RawIir
from ...container import SampleType, Container2D
from ...iir import IIR
from ...debuggers.value import AbstractValue


class JuceAudioBuffer(Container2D):
    __REGEX = rf"^(?:const\s+)?juce::AudioBuffer<{SampleType.regex()}>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
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

    def shape(self) -> Tuple[int, int]:
        return (self.num_channels, self.block_size)

    def __channel_data_ptr(self, channel: int) -> int:
        return int(self._value.attr("channels")[channel])

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


class JuceAudioBlock(Container2D):
    __REGEX = rf"^(?:const\s+)?juce::dsp::AudioBlock<{SampleType.regex()}>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
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

    def shape(self) -> Tuple[int, int]:
        return (self.num_channels, self.block_size)

    def __channel_data_ptr(self, channel: int) -> int:
        start = int(self._value.attr("startSample"))
        return self._value.attr("channels")[channel][start].address()

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


class JuceIIRCoefficients(IIR):
    __REGEX = rf"^(?:const\s+)?juce::dsp::IIR::Coefficients<{SampleType.regex()}>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {typename} as a valid juce::dsp::IIR::Coefficients type"
            )

        self._value = dbg_value
        datatype = SampleType.parse(re_match.group(1))
        super().__init__(dbg_value, name, datatype)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @property
    def num_coeffs(self) -> int:
        assert isinstance(self._value, AbstractValue)
        return int(self._value.attr("coefficients").attr("values").attr("numUsed"))

    @property
    def data_ptr(self) -> int:
        return int(
            self._value.attr("coefficients")
            .attr("values")
            .attr("elements")
            .attr("data")
        )

    def shape(self) -> Tuple[int, int]:
        return (1, self.num_coeffs)

    def read_from_debugger(self) -> RawIir.SOSCoeffs:
        byte_size = self.float_type.byte_size() * self.num_coeffs
        byte_array = self._value.readmemory(self.data_ptr, byte_size)
        fmt = "".join([self.float_type.struct_name() for _ in range(self.num_coeffs)])
        coeffs = struct.unpack(fmt, byte_array)
        if self.num_coeffs == 3:
            return RawIir.SOSCoeffs(
                [
                    (coeffs[0], coeffs[1], 0, 1.0, coeffs[2], 0),
                ]
            )
        else:
            return RawIir.SOSCoeffs(
                [
                    (coeffs[0], coeffs[1], coeffs[2], 1.0, coeffs[3], coeffs[4]),
                ]
            )


class JuceIIRFilter(IIR):
    __REGEX = rf"^(?:const\s+)?juce::dsp::IIR::Filter<{SampleType.regex()}>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {typename} as a valid juce::dsp::IIR::Filter type"
            )

        self._value = dbg_value
        datatype = SampleType.parse(re_match.group(1))
        super().__init__(dbg_value, name, datatype)
        self.__inner_coeffs = JuceIIRCoefficients(
            dbg_value.attr("coefficients").attr("referencedObject")[0],
            name + ".coefficients",
        )

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_from_debugger(self) -> RawIir.SOSCoeffs:
        return self.__inner_coeffs.read_from_debugger()


class JuceSVFCoefficientsOld(IIR):
    __REGEX = rf"^(?:const\s+)?juce::dsp::StateVariableFilter::Parameters<{SampleType.regex()}>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {typename} as a valid juce::dsp::StateVariableFilter::Parameters type"
            )

        self._value = dbg_value
        datatype = SampleType.parse(re_match.group(1))
        super().__init__(dbg_value, name, datatype)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_from_debugger(self) -> RawIir.SVFTPTCoeffs:
        g = float(self._value.attr("g"))
        r = float(self._value.attr("R2")) / 2
        ftype_int = int(self._value.attr("type"))
        if ftype_int == 0:
            ftype = RawIir.SVFTPTCoeffs.FilterType.LP
        elif ftype_int == 1:
            ftype = RawIir.SVFTPTCoeffs.FilterType.BP
        else:
            ftype = RawIir.SVFTPTCoeffs.FilterType.HP
        return RawIir.SVFTPTCoeffs(g, r, ftype)


class JuceSVFFilterOld(IIR):
    __REGEX = rf"^(?:const\s+)?juce::dsp::StateVariableFilter::Filter<{SampleType.regex()}>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {typename} as a valid juce::dsp::StateVariableFilter::Filter type"
            )

        self._value = dbg_value
        datatype = SampleType.parse(re_match.group(1))
        super().__init__(dbg_value, name, datatype)
        self.__inner_coeffs = JuceSVFCoefficientsOld(
            dbg_value.attr("parameters").attr("referencedObject")[0],
            name + ".parameters",
        )

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_from_debugger(self) -> RawIir.SVFTPTCoeffs:
        return self.__inner_coeffs.read_from_debugger()


class JuceSVFFilter(IIR):
    __REGEX = (
        rf"^(?:const\s+)?juce::dsp::StateVariableTPTFilter<{SampleType.regex()}>\s*$"
    )

    def __init__(self, dbg_value: AbstractValue, name: str, _=[]):
        typename = dbg_value.typename()
        re_match = self.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"Could not parse {typename} as a valid juce::dsp::StateVariableTPTFilter type"
            )

        self._value = dbg_value
        datatype = SampleType.parse(re_match.group(1))
        super().__init__(dbg_value, name, datatype)

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_from_debugger(self) -> RawIir.SVFTPTCoeffs:
        g = float(self._value.attr("g"))
        r = float(self._value.attr("R2")) / 2
        ftype_int = int(self._value.attr("filterType"))
        if ftype_int == 0:
            ftype = RawIir.SVFTPTCoeffs.FilterType.LP
        elif ftype_int == 1:
            ftype = RawIir.SVFTPTCoeffs.FilterType.BP
        else:
            ftype = RawIir.SVFTPTCoeffs.FilterType.HP
        return RawIir.SVFTPTCoeffs(g, r, ftype)


JuceAudioBuffer.register()
JuceAudioBlock.register()
JuceIIRCoefficients.register()
JuceIIRFilter.register()
JuceSVFCoefficientsOld.register()
JuceSVFFilterOld.register()
JuceSVFFilter.register()
