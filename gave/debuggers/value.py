from abc import ABC, abstractmethod


class AbstractValue(ABC):
    @abstractmethod
    def get(self):
        pass
