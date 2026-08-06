from ..core.element import Container, Element, Entity


class IdentifiedElement(Entity):
    def __init__(self, id: str):
        self._id = id

    @property
    def id(self) -> str:
        return self._id


class ManagedContainer(Container):
    def __init__(self):
        self._children: list[Element] = []

    @property
    def children(self) -> tuple[Element, ...]:
        return tuple(self._children)

    def attach(self, element: Element) -> None:
        self._children.append(element)

    def detach(self, element: Element) -> None:
        self._children.remove(element)


class IdentifiedContainer(IdentifiedElement, ManagedContainer):
    def __init__(self, id: str):
        IdentifiedElement.__init__(self, id)
        ManagedContainer.__init__(self)
