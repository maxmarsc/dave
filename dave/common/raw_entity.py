from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Union


@dataclass
class RawEntity(ABC):
    """
    The base class of a pickable representation of an Audio Concept visualizable
    by dave.

    It should contains all the information we can extract for the debugged process
    to render the concept in the GUI
    """

    id: int
    name: str
    in_scope: bool

    @abstractmethod
    def channels(self) -> int:
        pass

    @staticmethod
    @abstractmethod
    def supports_concat() -> bool:
        pass

    @dataclass
    class InScopeUpdate(ABC):
        """
        The base class of an inscope update used to send an update to the GUI
        """

        pass

    @dataclass
    class OutScopeUpdate:
        """
        Used to send an out-of-scope update to the GUI
        """

        id: int

    @abstractmethod
    def update(self, update: InScopeUpdate):
        """
        Updates the pickable representation with the content of the update
        """
        pass

    @abstractmethod
    def as_update(self) -> InScopeUpdate:
        pass


@dataclass
class RawEntityList:
    raw_entities: List[RawEntity]


@dataclass
class RawEntityUpdates:
    raw_updates: List[Union[RawEntity.InScopeUpdate, RawEntity.OutScopeUpdate]]
