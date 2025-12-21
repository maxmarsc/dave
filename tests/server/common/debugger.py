from abc import ABC, abstractmethod


class DebuggerAbstraction(ABC):
    @abstractmethod
    def set_breakpoint(self, location: str):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def continue_(self):
        pass

    @abstractmethod
    def execute(self, command: str) -> str:
        pass
