from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import re
from typing import Any, Callable, List, Tuple, Type, Union

# from .data_layout import DataLayout
from .sample_type import SampleType
from .raw_entity import RawEntity


@dataclass
class RawContainer(RawEntity):
    """
    A pickable representation of a container, sendable between the two dave process

    This should contains every piece of information needed by the GUI
    """

    default_layout: Layout
    possible_layout: List[Layout]
    # id: int
    data: bytearray
    # name: str
    original_shape: Tuple[int, int]
    dimensions_fixed: bool
    interleaved: bool
    sample_type: SampleType

    def channels(self):
        return (
            self.original_shape[0] if not self.interleaved else self.original_shape[1]
        )

    @staticmethod
    def supports_concat() -> bool:
        return True

    class Layout(Enum):
        REAL_1D = "Scalar 1D"
        REAL_2D = "Scalar 2D"
        CPX_1D = "Complex 1D"
        CPX_2D = "Complex 2D"

        @property
        def is_real(self) -> bool:
            return self in (
                RawContainer.Layout.REAL_1D,
                RawContainer.Layout.REAL_2D,
            )

    @dataclass
    class InScopeUpdate(RawEntity.InScopeUpdate):
        """
        Used to send a data update to the GUI
        """

        id: int
        data: bytearray
        shape: Tuple[int, int]

    # @dataclass
    # class OutScopeUpdate:
    #     """
    #     Used to send an out-of-scope update to the GUI
    #     """

    #     id: int

    def update(self, update: InScopeUpdate):
        assert self.id == update.id
        self.data = update.data
        self.original_shape = update.shape

    def as_update(self) -> InScopeUpdate:
        return RawContainer.InScopeUpdate(self.id, self.data, self.original_shape)
