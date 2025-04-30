from typing import Dict
from dave.common.singleton import SingletonMeta
from dave.common.raw_entity import RawEntity
from .entity_model import EntityModel


class ModelFactory(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.__entity_classes: Dict[type[RawEntity], type[EntityModel]] = dict()

    def register(self, raw_cls: type[RawEntity], model_cls: type[EntityModel]):
        assert issubclass(model_cls, EntityModel)
        assert issubclass(raw_cls, RawEntity)
        if raw_cls in self.__entity_classes:
            raise KeyError(
                f"Error: {raw_cls} was already registed in the model factory"
            )
        self.__entity_classes[raw_cls] = model_cls

    def build(self, raw_entity: RawEntity) -> EntityModel:
        assert isinstance(raw_entity, RawEntity)
        return self.__entity_classes[type(raw_entity)](raw_entity)
