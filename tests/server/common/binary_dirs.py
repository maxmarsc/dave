import os
from pathlib import Path
from abc import ABC, abstractmethod


class Binary(ABC):
    pass

    @abstractmethod
    def resolve(self) -> Path:
        pass


class CCppBinary(Binary):
    __BASE = os.environ.get("C_CPP_BIN_DIR", None)

    def __init__(self, filename: str):
        self.__filename = filename

    def resolve(self) -> Path:
        if not CCppBinary.__BASE:
            raise EnvironmentError("C_CPP_BIN_DIR environment variable is not set.")
        return (Path(CCppBinary.__BASE) / self.__filename).resolve()


class RustBinary(Binary):
    __BASE = os.environ.get("RUST_BIN_DIR", None)

    def __init__(self, filename: str):
        self.__filename = filename

    def resolve(self) -> Path:
        if not RustBinary.__BASE:
            raise EnvironmentError("RUST_BIN_DIR environment variable is not set.")
        return (Path(RustBinary.__BASE) / self.__filename).resolve()
