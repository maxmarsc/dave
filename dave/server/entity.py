from __future__ import annotations
from abc import ABC, abstractmethod
import re
from typing import Callable, Union

from dave.common.raw_entity import RawEntity
from dave.common.sample_type import SampleType

from .debuggers.value import AbstractValue


class EntityBuildError(Exception):
    pass


class Entity(ABC):
    """
    The base generalization of audio concepts : containers, filter...

    _extended_summary_
    """

    __count = -1

    @staticmethod
    def _new_id() -> int:
        Entity.__count += 1
        return Entity.__count

    def __init__(self, dbg_value: AbstractValue, name: str, sample_type: SampleType):
        self._value = dbg_value
        self.__name = name
        self.__id = Entity._new_id()
        self.__sample_type = sample_type

    @property
    def in_scope(self) -> bool:
        if isinstance(self._value, AbstractValue):
            return self._value.in_scope()
        return True

    @property
    def id(self) -> int:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def sample_type(self) -> SampleType:
        return self.__sample_type

    @abstractmethod
    def as_raw(self) -> RawEntity:
        """
        Builds a pickable representation of the entity to be send to the GUI
        """
        pass

    @abstractmethod
    def as_empty_raw(self) -> RawEntity:
        """
        Builds an empty (meaning no samples and out of scope) pickable representation of the entity to be send to the GUI
        """
        pass

    @classmethod
    def register(cls):
        """
        Register this entity class in DAVE

        1. Register the class to be available in the EntityFactory
        2. If the container should have a sparkline summary then it is registered
        in the debugger
        """
        from .entity_factory import EntityFactory

        EntityFactory().register(cls)

    @staticmethod
    @abstractmethod
    def formatter_compatible() -> bool:
        pass

    @staticmethod
    @abstractmethod
    def is_nested() -> bool:
        pass

    @classmethod
    @abstractmethod
    def typename_matcher(cls) -> Union[re.Pattern, Callable[[str], bool]]:
        pass

    @staticmethod
    @abstractmethod
    def supports_concat() -> bool:
        pass
