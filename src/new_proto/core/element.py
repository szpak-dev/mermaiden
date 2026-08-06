from new_proto.interface import Interface


class Element(Interface):
    """A thing that exists within a diagram and may combine element capabilities."""

    pass


class Container(Element):
    """An element that owns direct child elements through the containment tree.

    Ownership is distinct from diagram membership: every child remains available
    through the containing diagram's complete element collection.
    """

    @Interface.prop
    def children(self) -> tuple[Element, ...]: ...

    @Interface.method
    def add_child(self, element: Element) -> None: ...

    @Interface.method
    def remove_child(self, element: Element) -> None: ...


class Entity(Element):
    """An element with an identifier meaningful within its diagram.

    Identifier uniqueness is a diagram constraint, not an Entity responsibility.
    """

    @Interface.prop
    def id(self) -> str: ...
