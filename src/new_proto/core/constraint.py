from abc import abstractmethod
from typing import Protocol, runtime_checkable

from .diagram import Diagram
from .element import Element
from .relation import Relation


@runtime_checkable
class Constraint(Protocol):
    @abstractmethod
    def is_satisfied_by(self, diagram: Diagram) -> bool:
        raise NotImplementedError


@runtime_checkable
class ElementPresence(Constraint):
    element: type[Element]

    def is_satisfied_by(self, diagram: Diagram) -> bool:
        raise NotImplementedError


@runtime_checkable
class RelationDegree(Constraint):
    relation: type[Relation]

    def is_satisfied_by(self, diagram: Diagram) -> bool:
        raise NotImplementedError