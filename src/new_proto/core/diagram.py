from new_proto.interface import Interface

from .element import Element
from .relation import Relation


class Diagram(Interface):
    def elements(self) -> tuple[Element, ...]: ...
    def relations(self) -> tuple[Relation, ...]: ...
