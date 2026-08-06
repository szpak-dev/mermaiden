from abc import abstractmethod

from .base import Element


class Entity(Element):
    @property
    @abstractmethod
    def id(self) -> str:
        pass
