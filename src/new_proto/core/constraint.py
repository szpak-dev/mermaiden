from new_proto.interface import Interface

from .element import Element
from .diagram import DiagramContents
from .relation import DirectedRelation, Relation


class Constraint(Interface):
    """A declarative rule evaluated against diagram contents without changing them."""

    @Interface.method
    def is_satisfied_by(self, diagram_contents: DiagramContents) -> bool: ...


class ElementPresence(Constraint):
    """Constrains the allowed number of instances of an element type."""

    @Interface.prop
    def element(self) -> type[Element]: ...

    @Interface.prop
    def minimum(self) -> int: ...

    @Interface.prop
    def maximum(self) -> int | None: ...


class RelationDegree(Constraint):
    """Constrains relations of a type in which an element type is a participant."""

    @Interface.prop
    def element(self) -> type[Element]: ...

    @Interface.prop
    def relation(self) -> type[Relation]: ...

    @Interface.prop
    def minimum(self) -> int: ...

    @Interface.prop
    def maximum(self) -> int | None: ...


class IncomingRelationDegree(RelationDegree):
    """Constrains directed relations in which an element is their target."""

    @Interface.prop
    def relation(self) -> type[DirectedRelation]: ...


class OutgoingRelationDegree(RelationDegree):
    """Constrains directed relations in which an element is their source."""

    @Interface.prop
    def relation(self) -> type[DirectedRelation]: ...
