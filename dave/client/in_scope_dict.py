from typing import Dict, Set
from PySide6.QtCore import QObject, Signal

from dave.client.entity.entity_model import EntityModel


class InScopeSet(QObject):
    scope_signal = Signal(int, bool)

    def __init__(self):
        super().__init__()
        # self.__set: Dict[int, EntityModel] = dict()
        self.__set: Set[int] = set()

    def add(self, model: EntityModel):
        assert model.in_scope
        assert model.id not in self.__set
        # self.__set[model.id] = model
        self.__set.add(model.id)
        self.scope_signal.emit(model.id, True)

    def remove(self, model: EntityModel):
        assert model.id in self.__set
        assert model.in_scope
        self.__set.remove(model.id)
        self.scope_signal.emit(model.id, False)

    def has(self, id: int) -> bool:
        return id in self.__set

    def get(self) -> Set[int]:
        return self.__set
