from new_proto.interface import Interface

from .element import Container, Element
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
    """The sole authority for a diagram's composition and its consistency."""

    @Interface.method
    def contents(self) -> DiagramContents:
        """Returns the diagram's read-only composition."""

        ...

    @Interface.method
    def add_element(self, element: Element, *, owner: Container | None = None) -> None:
        """Adds an element and, when given, makes an existing container its owner."""

        ...

    @Interface.method
    def remove_element(self, element: Element) -> None:
        """Removes an element, its owned subtree, and all related relations."""

        ...

    @Interface.method
    def add_relation(self, relation: Relation) -> None:
        """Adds a relation only when all its participants belong to the diagram."""

        ...

    @Interface.method
    def remove_relation(self, relation: Relation) -> None:
        """Removes a relation from the diagram."""

        ...
