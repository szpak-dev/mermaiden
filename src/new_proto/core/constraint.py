from new_proto.interface import Interface

from .element import Element
from .diagram import DiagramContents
from .relation import Relation


class Constraint(Interface):
    """A rule about complete diagram composition, not behavior of one entity."""

    @Interface.method
    def is_satisfied_by(self, diagram_contents: DiagramContents) -> bool: ...


class ElementPresence(Constraint):
    """Constrains the allowed number of elements of a given type in a diagram."""

    @Interface.prop
    def element(self) -> type[Element]: ...

    @Interface.prop
    def minimum(self) -> int: ...

    @Interface.prop
    def maximum(self) -> int | None: ...


class RelationDegree(Constraint):
    """Constrains how many relations of a given type involve an element type."""

    @Interface.prop
    def element(self) -> type[Element]: ...

    @Interface.prop
    def relation(self) -> type[Relation]: ...

    @Interface.prop
    def minimum(self) -> int: ...

    @Interface.prop
    def maximum(self) -> int | None: ...
