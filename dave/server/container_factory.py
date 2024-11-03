import re
from typing import Any, List, Dict, Set, Union

from dave.common.logger import Logger

from dave.common.singleton import SingletonMeta
from .container import Container, Container1D, Container2D
from .debuggers.value import AbstractValue


class ContainerError(Exception):
    pass


class ContainerFactory(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.__1D_containers: Set[Container1D] = set()
        self.__2D_containers: Set[Container2D] = set()

    def register(self, cls):
        """
        Every new container class should register itself to be available
        at debugger runtime.
        """
        try:
            if issubclass(cls, Container1D):
                if cls in self.__1D_containers:
                    raise KeyError
                self.__1D_containers.add(cls)
            elif issubclass(cls, Container2D):
                if cls in self.__2D_containers:
                    raise KeyError
                self.__2D_containers.add(cls)
            else:
                raise ContainerError(
                    f"Error : {cls} is not a valid subclass of Container"
                )
        except KeyError:
            raise ContainerError(
                f"Error : {cls} was already registered in the container factory"
            )

    def check_valid_1D(self, typename: str) -> bool:
        """
        Returns true if the given typename matches a registered 1D container class
        """
        for container_1D_cls in self.__1D_containers:
            pattern = container_1D_cls.typename_matcher()
            if (
                isinstance(pattern, re.Pattern) and pattern.match(typename) is not None
            ) or (callable(pattern) and pattern(typename)):
                return True

        return False

    def build_1D(
        self,
        dbg_value: AbstractValue,
        typename: str,
        varname: str,
        dims: List[int] = [],
    ) -> Container1D:
        """
        Try to build a 1D Container object from a debugger value

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
        for container_1D_cls in self.__1D_containers:
            new_container = self.__build_if_match(
                container_1D_cls, dbg_value, typename, varname, dims
            )
            if new_container is not None:
                return new_container

        raise ContainerError(
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
            return self.build_1D(dbg_value, typename, varname, dims)
        except (ContainerError, TypeError):
            Logger().debug(f"{typename} is not a valid 1D container")
            pass

        # Then we check for 2D containers
        for container_2D_cls in self.__2D_containers:
            new_container = self.__build_if_match(
                container_2D_cls, dbg_value, typename, varname, dims
            )
            if new_container is not None:
                return new_container

        raise ContainerError(
            f"Error : {typename} did not match any registered container class"
        )

    def __build_if_match(
        self,
        container_cls: Container,
        dbg_value: Any,
        typename: str,
        varname: str,
        dims: List[int],
    ):
        pattern = container_cls.typename_matcher()
        if (
            isinstance(pattern, re.Pattern) and pattern.match(typename) is not None
        ) or (callable(pattern) and pattern(typename)):
            return container_cls(dbg_value, varname, dims)
        return None
