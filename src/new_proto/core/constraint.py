from typing import runtime_checkable

from .base import Constraint, Diagram, Element, Relation


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