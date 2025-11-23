from __future__ import annotations

import re
from typing import Tuple

from ...container import SampleType, Container2D
from ...debuggers.value import AbstractValue
from dave.server.languages import c_cpp

class HartAudioBuffer(Container2D):
    __REGEX = rf"^(?:const\s+)?hart::AudioBuffer<{SampleType.regex()}>\s*$"

    def __init__(self, dbg_value: AbstractValue, name: str, _):
        typename = dbg_value.typename()
        sample_type, *_ = self._parse_typename(typename)
        super().__init__(dbg_value, name, sample_type)

    @property
    def __inner(self) -> c_cpp.StdVector1D:
        return c_cpp.StdVector1D(self._value.attr("m_frames"), self.name + ".m_frames")

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    @classmethod
    def _parse_typename(cls, typename: str, **_) -> Tuple[SampleType, None, None]:
        re_match = cls.typename_matcher().match(typename)
        if re_match is None:
            raise TypeError(
                f"HartAudioBuffer could not parse {typename} as a valid type"
            )

        return (SampleType.parse(re_match.group(1)), None, None)

    def shape(self) -> Tuple[int, int]:
        assert isinstance(self._value, AbstractValue)
        try:
            return (
                int(self._value.attr("m_numChannels")),
                int(self._value.attr("m_numFrames"))
            )
        except:
            raise RuntimeError(f"Failed to retrieve shape of {self._value.typename()}")

    def read_from_debugger(self) -> bytearray:
        return self.__inner.read_from_debugger()

HartAudioBuffer.register()
