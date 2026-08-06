from new_proto.interface import Interface

from .element import Element
from .query import DiagramQuery
from .relation import Relation


class Constraint(Interface):
    def is_satisfied_by(self, diagram: DiagramQuery) -> bool: ...


class ElementPresence(Constraint):
    element: type[Element]
    minimum: int
    maximum: int | None


class RelationDegree(Constraint):
    element: type[Element]
    relation: type[Relation]
    minimum: int
    maximum: int | None
