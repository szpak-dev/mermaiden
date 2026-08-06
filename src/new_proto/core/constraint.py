from new_proto.interface import Interface

from .diagram import Diagram
from .element import Element
from .relation import Relation


class Constraint(Interface):
    def is_satisfied_by(self, diagram: Diagram) -> bool: ...


class ElementPresence(Constraint):
    element: type[Element]


class RelationDegree(Constraint):
    relation: type[Relation]
