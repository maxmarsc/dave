import re
from typing import Any, List, Dict, Set, Union

from dave.common.logger import Logger

from dave.common.singleton import SingletonMeta
from .entity import Entity
from .container import Container, Container1D, Container2D
from .debuggers.value import AbstractValue


class EntityBuildError(Exception):
    pass


class EntityFactory(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.__simple_entity_classes: Set[type[Entity]] = set()
        self.__nested_entity_classes: Set[type[Entity]] = set()

    def get_containers_cls_set(self) -> Set[type[Entity]]:
        return self.__simple_entity_classes | self.__nested_entity_classes

    def register(self, cls):
        """
        Every new container class should register itself to be available
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

    def check_valid_simple(self, typename: str) -> bool:
        """
        Returns true if the given typename matches a registered simple container class
        """
        for simple_entity_cls in self.__simple_entity_classes:
            pattern = simple_entity_cls.typename_matcher()
            if (
                isinstance(pattern, re.Pattern) and pattern.match(typename) is not None
            ) or (callable(pattern) and pattern(typename)):
                return True

        return False

    def build_simple(
        self,
        dbg_value: AbstractValue,
        typename: str,
        varname: str,
        dims: List[int] = [],
    ) -> Container1D:
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
        for container_1D_cls in self.__simple_entity_classes:
            new_container = self.__build_if_match(
                container_1D_cls, dbg_value, typename, varname, dims
            )
            if new_container is not None:
                return new_container

        raise EntityBuildError(
            f"Error : {typename} did not match any registered 1D container class"
        )

    def build(
        self,
        dbg_value: AbstractValue,
        typename: str,
        varname: str,
        dims: List[int] = [],
    ) -> Container:
        """
        Try to build a Container object from a debugger value

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
        Container
            A valid Container, either 1D or 2D subclass instance pointing to the debugger memory

        Raises
        ------
        ContainerError
            If no registered class matched the typename
        """
        Logger().debug(f"Building {varname} from type |{typename}|")

        # First we check if it is a 1D container
        try:
            return self.build_simple(dbg_value, typename, varname, dims)
        except (EntityBuildError, TypeError):
            Logger().debug(f"{typename} is not a valid 1D container")
            pass

        # Then we check for 2D containers
        for nested_entity in self.__nested_entity_classes:
            new_entity = self.__build_if_match(
                nested_entity, dbg_value, typename, varname, dims
            )
            if new_entity is not None:
                return new_entity

        raise EntityBuildError(
            f"Error : {typename} did not match any registered container class"
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
