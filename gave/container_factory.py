import re
import gdb  # type: ignore
from typing import Any, List, Dict, Set, Union

from .singleton import SingletonMeta
from .container import Container, Container1D, Container2D


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
                raise gdb.GdbError(
                    f"Error : {cls} is not a valid subclass of Container"
                )
        except KeyError:
            raise gdb.GdbError(
                f"Error : {cls} was already registered in the container factory"
            )

    def check_valid_1D(self, typename: str) -> bool:
        for container_1D_cls in self.__1D_containers:
            if container_1D_cls.regex_name().match(typename) is not None:
                return True

        return False

    def build_1D(
        self, gdb_value: gdb.Value, name: str, dims: List[int] = []
    ) -> Container1D:
        typename = str(gdb.types.get_basic_type(gdb_value.type))

        for container_1D_cls in self.__1D_containers:
            if container_1D_cls.regex_name().match(typename) is not None:
                return container_1D_cls(gdb_value, name, dims)

        raise gdb.GdbError(
            f"Error : {typename} did not match any registered 1D container class"
        )

    def build(self, gdb_value: gdb.Value, name: str, dims: List[int] = []) -> Container:
        typename = str(gdb.types.get_basic_type(gdb_value.type))

        # First we check if it is a 1D container
        try:
            return self.build_1D(gdb_value, name, dims)
        except gdb.GdbError:
            pass

        # Then we check for 2D containers
        for container_2D_cls in self.__2D_containers:
            if container_2D_cls.regex_name().match(typename) is not None:
                return container_2D_cls(gdb_value, name, dims)

        raise gdb.GdbError(
            f"Error : {typename} did not match any registered container class"
        )
