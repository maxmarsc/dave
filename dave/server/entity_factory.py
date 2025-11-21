from collections import defaultdict
import re
from typing import Any, DefaultDict, List, Dict, Set, Union

from dave.common.logger import Logger

from dave.common.singleton import SingletonMeta
from .entity import Entity, EntityBuildError
from .debuggers.value import AbstractValue
from .language_type import LanguageType


class EntityFactory(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.__simple_entity_classes: DefaultDict[LanguageType, Set[type[Entity]]] = (
            defaultdict(set)
        )
        self.__nested_entity_classes: DefaultDict[LanguageType, Set[type[Entity]]] = (
            defaultdict(set)
        )

    def get_entities_cls_set(self) -> Set[type[Entity]]:
        full_set: Set[type[Entity]] = set()
        for simple_lang_set in self.__simple_entity_classes.values():
            full_set = full_set | simple_lang_set
        for nested_lang_set in self.__nested_entity_classes.values():
            full_set = full_set | nested_lang_set
        return full_set

    def register(self, cls: type[Entity], lang: LanguageType):
        """
        Register a new entity class for a given software language.

        Every Entity class must be registered to be available at debug

        Parameters
        ----------
        cls : type[Entity]
            The entity class to register. Can be simple or nested
        lang : LanguageType
            The corresponding language for the given entity. If the language
            is set to LanguageType.C it will be register for both C and C++ languages

        Raises
        ------
        EntityBuildError
            If the entity class was already registered
        """
        assert issubclass(cls, Entity)
        assert lang != LanguageType.UNSUPPORTED
        langs = (
            [LanguageType.C, LanguageType.CPP]
            if lang == LanguageType.C
            else [
                lang,
            ]
        )
        try:
            if not cls.is_nested():
                # print(f"REGISTER: {lang}:{cls}")
                for lang in langs:
                    # print(f"REGISTER: {self.__simple_entity_classes[lang]}")
                    if cls in self.__simple_entity_classes[lang]:
                        raise KeyError(lang.name)
                    self.__simple_entity_classes[lang].add(cls)
            else:
                for lang in langs:
                    if cls in self.__nested_entity_classes[lang]:
                        raise KeyError(lang.name)
                    self.__nested_entity_classes[lang].add(cls)
        except KeyError as e:
            raise EntityBuildError(
                f"Error : {cls} was already registered in the container factory: {e}"
            )

    def check_valid_simple(self, typename: str) -> Union[type[Entity], None]:
        """
        Returns true if the given typename matches a registered simple entity class
        """
        for simple_entity_set in self.__simple_entity_classes.values():
            for simple_entity_cls in simple_entity_set:
                pattern = simple_entity_cls.typename_matcher()
                if (
                    isinstance(pattern, re.Pattern)
                    and pattern.match(typename) is not None
                ) or (callable(pattern) and pattern(typename)):
                    return simple_entity_cls

        return None

    def build_simple(
        self,
        dbg_value: AbstractValue,
        typename: str,
        varname: str,
        dims: List[int] = [],
    ) -> Entity:
        """
        Try to build a simple Container object from a debugger value

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
        Entity
            A valid Entity subclass instance pointing to the debugger memory

        Raises
        ------
        ContainerError
            If no registered class matched the typename
        """
        assert dbg_value.language() != LanguageType.UNSUPPORTED
        for simple_entity_cls in self.__simple_entity_classes[dbg_value.language()]:
            new_container = self.__build_if_match(
                simple_entity_cls, dbg_value, typename, varname, dims
            )
            if new_container is not None:
                return new_container

        raise EntityBuildError(
            f"Error : {typename} did not match any registered simple Entity class"
        )

    def build(
        self,
        dbg_value: AbstractValue,
        typename: str,
        varname: str,
        dims: List[int] = [],
    ) -> Entity:
        """
        Try to build a Entity from a debugger value

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
        Entity
            A valid Entity, pointing to the debugger memory

        Raises
        ------
        EntityBuildError
            If no registered class matched the typename
        """
        assert dbg_value.language() != LanguageType.UNSUPPORTED
        Logger().debug(f"Building {varname} from type |{typename}|")

        # First we check if it is a simple (not nested) class
        try:
            return self.build_simple(dbg_value, typename, varname, dims)
        except EntityBuildError as e:
            Logger().debug(f"{typename} is not a valid simple Entity class")
            pass
        except TypeError as e:
            raise EntityBuildError(f"Failed to build {typename} with {e}")

        # Then we check for nested entity classes
        for nested_entity in self.__nested_entity_classes[dbg_value.language()]:
            new_entity = self.__build_if_match(
                nested_entity, dbg_value, typename, varname, dims
            )
            if new_entity is not None:
                return new_entity

        raise EntityBuildError(
            f"Error : {typename} did not match any registered Entity class"
        )

    def __build_if_match(
        self,
        entity_cls: type[Entity],
        dbg_value: Any,
        typename: str,
        varname: str,
        dims: List[int],
    ):
        pattern = entity_cls.typename_matcher()
        if (
            isinstance(pattern, re.Pattern) and pattern.match(typename) is not None
        ) or (callable(pattern) and pattern(typename)):
            return entity_cls(dbg_value, varname, dims)
        return None
