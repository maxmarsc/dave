from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List


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
    default_layout: Layout
    possible_layout: List[Layout]

    @abstractmethod
    def channels(self) -> int:
        pass

    class Layout(Enum):
        # Cannot inherit from both Enum and ABC metaclass
        """
        The layout subclass should enumerate the different memory layout possible
        for a specific audio concept
        """

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
