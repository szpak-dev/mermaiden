from new_proto.interface import Interface

from .element import Element


class Relation(Interface):
    """A connection between elements, independent of containment ownership.

    A relation is neither an Element nor a child of a container. Its
    participants are every element to which the relation refers.
    """

    @Interface.prop
    def participants(self) -> tuple[Element, ...]: ...


class DirectedRelation(Relation):
    """A relation between exactly two participants with distinct endpoint roles."""

    @Interface.prop
    def source(self) -> Element: ...

    @Interface.prop
    def target(self) -> Element: ...


class Association(Relation):
    """A relation among participants without universal endpoint roles."""

    pass
