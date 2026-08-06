from new_proto.interface import Interface

from .element import Element
from .relation import Relation


class DiagramQuery(Interface):
    """Read-only access to every element and relation available in a diagram.

    The element collection is the full diagram membership, including elements
    owned by nested containers.
    """

    @Interface.prop
    def elements(self) -> tuple[Element, ...]: ...

    @Interface.prop
    def relations(self) -> tuple[Relation, ...]: ...
