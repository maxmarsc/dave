import re
from typing import Any, List, Dict, Set, Union

from dave.common.logger import Logger

from dave.common.singleton import SingletonMeta
from .entity import Entity, EntityBuildError
from .container import Container, Container1D, Container2D
from .debuggers.value import AbstractValue


class EntityFactory(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.__simple_entity_classes: Set[type[Entity]] = set()
        self.__nested_entity_classes: Set[type[Entity]] = set()

    def get_entities_cls_set(self) -> Set[type[Entity]]:
        return self.__simple_entity_classes | self.__nested_entity_classes

    def register(self, cls):
        """
        Every new entity class should register itself to be available
        at debugger runtime.
        """
        assert issubclass(cls, Entity)
        try:
            if not cls.is_nested():
                if cls in self.__simple_entity_classes:
                    raise KeyError
                self.__simple_entity_classes.add(cls)
            else:
                if cls in self.__nested_entity_classes:
                    raise KeyError
                self.__nested_entity_classes.add(cls)
        except KeyError:
            raise EntityBuildError(
                f"Error : {cls} was already registered in the container factory"
            )

    def check_valid_simple(self, typename: str) -> Union[type[Entity], None]:
        """
        Returns true if the given typename matches a registered simple entity class
        """
        for simple_entity_cls in self.__simple_entity_classes:
            pattern = simple_entity_cls.typename_matcher()
            if (
                isinstance(pattern, re.Pattern) and pattern.match(typename) is not None
            ) or (callable(pattern) and pattern(typename)):
                return simple_entity_cls

        return None

    def build_simple(
        self,
        dbg_value: AbstractValue,
        typename: str,
        varname: str,
        dims: List[int] = [],
    ) -> Entity:
        """
        Try to build a simple Container object from a debugger value

        Parameters
        ----------
        dbg_value : AbstractValue
            The debugger value of the container to build a wrapper for
        typename : str
            The typename of the corresponding values, typedef and aliases should
            be resolved
        varname : str
            The name of the variable in the program
        dims : List[int], optional
            Only needed for dimensionless containers, like pointers, by default []

        Returns
        -------
        Container1D
            A valid Container1D subclass instance pointing to the debugger memory

        Raises
        ------
        ContainerError
            If no registered class matched the typename
        """
        for simple_entity_cls in self.__simple_entity_classes:
            new_container = self.__build_if_match(
                simple_entity_cls, dbg_value, typename, varname, dims
            )
            if new_container is not None:
                return new_container

        raise EntityBuildError(
            f"Error : {typename} did not match any registered simple Entity class"
        )

    def build(
        self,
        dbg_value: AbstractValue,
        typename: str,
        varname: str,
        dims: List[int] = [],
    ) -> Entity:
        """
        Try to build a Entity from a debugger value

        Parameters
        ----------
        dbg_value : AbstractValue
            The debugger value of the container to build a wrapper for
        typename : str
            The typename of the corresponding values, typedef and aliases should
            be resolved
        varname : str
            The name of the variable in the program
        dims : List[int], optional
            Only needed for dimensionless containers, like pointers, by default []

        Returns
        -------
        Entity
            A valid Entity, pointing to the debugger memory

        Raises
        ------
        EntityBuildError
            If no registered class matched the typename
        """
        Logger().debug(f"Building {varname} from type |{typename}|")

        # First we check if it is a simple (not nested) class
        try:
            return self.build_simple(dbg_value, typename, varname, dims)
        except EntityBuildError as e:
            Logger().debug(f"{typename} is not a valid simple Entity class")
            pass
        except TypeError as e:
            raise EntityBuildError(f"Failed to build {typename} with {e}")

        # Then we check for nested entity classes
        for nested_entity in self.__nested_entity_classes:
            new_entity = self.__build_if_match(
                nested_entity, dbg_value, typename, varname, dims
            )
            if new_entity is not None:
                return new_entity

        raise EntityBuildError(
            f"Error : {typename} did not match any registered Entity class"
        )

    def __build_if_match(
        self,
        entity_cls: Entity,
        dbg_value: Any,
        typename: str,
        varname: str,
        dims: List[int],
    ):
        pattern = entity_cls.typename_matcher()
        if (
            isinstance(pattern, re.Pattern) and pattern.match(typename) is not None
        ) or (callable(pattern) and pattern(typename)):
            return entity_cls(dbg_value, varname, dims)
        return None
