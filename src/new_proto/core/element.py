from abc import abstractmethod

from .base import Element


class Container(Element):
    @property
    @abstractmethod
    def children(self) -> tuple[Element, ...]:
        pass


class Entity(Element):
    @property
    @abstractmethod
    def id(self) -> str:
        pass
