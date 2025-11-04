from typing import Dict, List, Set
from PySide6.QtCore import QObject, Signal

from dave.client.entity.entity_model import EntityModel
from dave.common.logger import Logger


class InScopeSet(QObject):
    scope_signal = Signal(list, bool)

    def __init__(self):
        super().__init__()
        self.__set: Set[int] = set()

    def add(self, models: List[EntityModel]):
        if len(models) == 0:
            return
        signal: List[int] = list()
        for model in models:
            assert model.in_scope
            assert model.id not in self.__set
            self.__set.add(model.id)
            signal.append(model.id)
        self.scope_signal.emit(signal, True)

    def remove(self, models: List[EntityModel]):
        if len(models) == 0:
            return
        signal: List[int] = list()
        for model in models:
            assert model.id in self.__set
            assert model.in_scope
            self.__set.remove(model.id)
            signal.append(model.id)
        self.scope_signal.emit(signal, False)

    def has(self, id: int) -> bool:
        return id in self.__set

    def get(self) -> Set[int]:
        return self.__set
