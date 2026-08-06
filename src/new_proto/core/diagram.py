from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from .element import Element
from .relation import Relation


class Diagram(ABC):
    @property
    @abstractmethod
    def elements(self) -> tuple[Element, ...]:
        pass

    @property
    @abstractmethod
    def relations(self) -> tuple[Relation, ...]:
        pass
