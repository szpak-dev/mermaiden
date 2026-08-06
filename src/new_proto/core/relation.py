from abc import abstractmethod

from .base import Element, Relation


class DirectedRelation(Relation):
    @property
    @abstractmethod
    def source(self) -> Element:
        pass

    @property
    @abstractmethod
    def target(self) -> Element:
        pass


class Association(Relation):
    @property
    @abstractmethod
    def participants(self) -> tuple[Element, ...]:
        pass
