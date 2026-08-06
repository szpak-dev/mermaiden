from abc import abstractmethod

from .base import Element


class Annotation(Element):
    @property
    @abstractmethod
    def targets(self) -> tuple[str, ...]:
        pass
