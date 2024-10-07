import re
from typing import Any, List, Dict, Set, Union

from dave.common.logger import Logger

from dave.common.singleton import SingletonMeta
from .container import Container, Container1D, Container2D


class ContainerError(Exception):
    pass


class ContainerFactory(metaclass=SingletonMeta):
    def __init__(self) -> None:
        # self.__buffer_list = {}
        self.__1D_containers: Set[Container1D] = set()
        self.__2D_containers: Set[Container2D] = set()

    def register(self, cls):
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
        for container_1D_cls in self.__1D_containers:
            if container_1D_cls.typename_matcher().match(typename) is not None:
                return True

        return False

    def build_1D(
        self, dbg_value: Any, typename: str, varname: str, dims: List[int] = []
    ) -> Container1D:
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
        self, dbg_value: Any, typename: str, varname: str, dims: List[int] = []
    ) -> Container:
        Logger().get().debug(f"Building {varname} from type |{typename}|")

        # First we check if it is a 1D container
        try:
            return self.build_1D(dbg_value, typename, varname, dims)
        except (ContainerError, TypeError):
            Logger().get().debug(f"{typename} is not a valid 1D container")
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
