from abc import abstractmethod

from .base import Element


class Relation(Element):
    @property
    @abstractmethod
    def endpoints(self) -> tuple[str, ...]:
        pass
