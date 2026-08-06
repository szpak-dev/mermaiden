from new_proto.interface import Interface

from .element import Element
from .relation import Relation


class DiagramContents(Interface):
    """Read-only access to every element and relation available in a diagram.

    The element collection is the full diagram membership, including elements
    owned by nested containers.
    """

    @Interface.prop
    def elements(self) -> tuple[Element, ...]: ...

    @Interface.prop
    def relations(self) -> tuple[Relation, ...]: ...


class Diagram(Interface):
    """Manages the membership of elements and relations in a diagram."""

    @Interface.method
    def contents(self) -> DiagramContents: ...

    @Interface.method
    def add_element(self, element: Element) -> None: ...

    @Interface.method
    def remove_element(self, element: Element) -> None: ...

    @Interface.method
    def add_relation(self, relation: Relation) -> None: ...

    @Interface.method
    def remove_relation(self, relation: Relation) -> None: ...



