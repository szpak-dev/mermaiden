from new_proto.interface import Interface

from .element import Element


class Relation(Interface):
    """A connection between elements, independent of containment ownership.

    A relation is neither an Element nor a child of a container.
    """

    pass


class DirectedRelation(Relation):
    """A relation with distinct source and target endpoint roles."""

    @Interface.prop
    def source(self) -> Element: ...

    @Interface.prop
    def target(self) -> Element: ...


class Association(Relation):
    """A relation among participants without a universal direction."""

    @Interface.prop
    def participants(self) -> tuple[Element, ...]: ...
