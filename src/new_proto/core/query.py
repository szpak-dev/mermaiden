from new_proto.interface import Interface

from .element import Element
from .relation import Relation


class DiagramQuery(Interface):
    @Interface.prop
    def elements(self) -> tuple[Element, ...]: ...

    @Interface.prop
    def relations(self) -> tuple[Relation, ...]: ...
