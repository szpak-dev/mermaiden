from new_proto.interface import Interface


class Element(Interface):
    """A thing that exists within a diagram and may combine element capabilities."""

    @Interface.prop
    def id(self) -> str: ...


class Entity(Element):
    """An element with an identifier meaningful within its diagram.

    Identifier uniqueness is a diagram constraint, not an Entity responsibility;
    the identifier is not globally scoped.
    """

    pass


class Container(Entity):
    """An element that owns direct child elements through the containment tree.

    It describes ownership but does not change it: the containing Diagram keeps
    this hierarchy and complete diagram membership consistent.
    """

    @Interface.prop
    def children(self) -> tuple[Element, ...]: ...
