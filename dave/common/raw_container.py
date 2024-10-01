from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import re
from typing import Any, Callable, List, Tuple, Type, Union

from .data_layout import DataLayout
from .sample_type import SampleType


@dataclass
class RawContainer:
    id: int
    data: bytearray
    name: str
    original_shape: Tuple[int, int]
    dimensions_fixed: bool
    sample_type: SampleType
    container_cls: Type
    default_layout: DataLayout
    possible_layout: List[DataLayout]

    @dataclass
    class InScopeUpdate:
        id: int
        data: bytearray
        shape: Tuple[int, int]

    @dataclass
    class OutScopeUpdate:
        id: int

    def update(self, update: InScopeUpdate):
        assert self.id == update.id
        self.data = update.data
        self.original_shape = update.shape
