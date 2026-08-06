from new_proto.interface import Interface

from .element import Element
from .query import DiagramQuery
from .relation import Relation


class Constraint(Interface):
    @Interface.method
    def is_satisfied_by(self, diagram: DiagramQuery) -> bool: ...


class ElementPresence(Constraint):
    @Interface.prop
    def element(self) -> type[Element]: ...

    @Interface.prop
    def minimum(self) -> int: ...

    @Interface.prop
    def maximum(self) -> int | None: ...


class RelationDegree(Constraint):
    @Interface.prop
    def element(self) -> type[Element]: ...

    @Interface.prop
    def relation(self) -> type[Relation]: ...

    @Interface.prop
    def minimum(self) -> int: ...

    @Interface.prop
    def maximum(self) -> int | None: ...
