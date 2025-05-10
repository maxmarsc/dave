from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List, Union


class Endianness(Enum):
    LITTLE = "<"
    BIG = ">"


class DebuggerMemoryError(Exception):
    """
    Represents an error in the memory representation of the debugged process.

    It might represent an error in accessing the memory or in the values
    of the accessed memory
    """

    pass


class AbstractValue(ABC):
    @abstractmethod
    def typename(self) -> str:
        pass

    @abstractmethod
    def varname(self) -> str:
        pass

    @abstractmethod
    def byte_size(self) -> int:
        pass

    @abstractmethod
    def attr(self, name: str) -> AbstractValue:
        pass

    @abstractmethod
    def address(self) -> int:
        pass

    @abstractmethod
    def __int__(self) -> int:
        pass

    @abstractmethod
    def __float__(self) -> float:
        pass

    @abstractmethod
    def __getitem__(self, key: int) -> AbstractValue:
        pass

    @abstractmethod
    def in_scope(self) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def readmemory(addr: int, bytesize: int) -> bytearray:
        pass

    @staticmethod
    @abstractmethod
    def find_variable(
        varname: str, where: Union[Any, None] = None
    ) -> Union[AbstractValue, None]:
        """
        Try to find a variable by its name. The user can provide a specific
        context to look for it.

        Parameters
        ----------
        varname : str
            The name of the symbol to look for.
        where : Union[Any, None], optional
            A context object used to indicate in which scope to look for the variable.
            If the value is None, it will search in the currently selected frame/scope,
            by default None

        Returns
        -------
        Union[AbstractValue, None]
            A valid AbstractValue object, or None if the variable was not found
        """
        pass

    @staticmethod
    @abstractmethod
    def find_all_variables(where: Union[Any, None]) -> List[AbstractValue]:
        """
        Parse all variables in the given frame, including ones not compatible with DAVE

        _extended_summary_

        Parameters
        ----------
        where : Union[Any, None]
            A context object used to indicate in which scope to look for the variable.
            If the value is None, it will search in the currently selected frame/scope,
            by default None

        Returns
        -------
        List[AbstractValue]
            A list of all the valid AbstractValue objects that were found in the
            context
        """
        pass
