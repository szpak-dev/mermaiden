from dataclasses import dataclass, replace

from wireup import injectable

from ...core.element import Container, Element, Entity
from ...core.error import OperationError
from .state import DiagramData, DiagramState


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Elements:
    state: DiagramState

    def add(self, element: Element, parent_id: str = "") -> DiagramData:
        elements = self._insert(self.state.current.elements, element, parent_id)
        return replace(self.state.current, elements=elements)

    def add_container(self, id: str, label: str, parent_id: str = "") -> DiagramData:
        return self.add(Container(id, label), parent_id)

    def add_entity(self, id: str, label: str, parent_id: str = "") -> DiagramData:
        return self.add(Entity(id, label), parent_id)

    def remove(self, id: str) -> tuple[DiagramData, tuple[str, ...]]:
        target = self.find(id)
        if target is None:
            raise OperationError(f"Element '{id}' does not exist.")
        removed = tuple(item.id for item in self._walk((target,)))
        elements = self._remove(self.state.current.elements, id)
        return replace(self.state.current, elements=elements), removed

    def find(self, id: str) -> Element | None:
        return next((item for item in self.walk() if item.id == id), None)

    def walk(self, parent_id: str = "") -> tuple[Element, ...]:
        roots = self.state.current.elements
        if parent_id:
            parent = self.find(parent_id)
            if not isinstance(parent, Container):
                return ()
            roots = parent.elements
        return self._walk(roots)

    def _insert(
        self,
        elements: tuple[Element, ...],
        element: Element,
        parent_id: str,
    ) -> tuple[Element, ...]:
        if not parent_id:
            return (*elements, element)
        parent = self.find(parent_id)
        if parent is None:
            raise OperationError(f"Parent element '{parent_id}' does not exist.")
        if not isinstance(parent, Container):
            raise OperationError(f"Parent element '{parent_id}' is not a container.")
        return self._append_child(elements, parent_id, element)

    def _append_child(
        self,
        elements: tuple[Element, ...],
        parent_id: str,
        child: Element,
    ) -> tuple[Element, ...]:
        result: list[Element] = []
        for element in elements:
            if element.id == parent_id and isinstance(element, Container):
                result.append(replace(element, elements=(*element.elements, child)))
            elif isinstance(element, Container):
                result.append(replace(element, elements=self._append_child(element.elements, parent_id, child)))
            else:
                result.append(element)
        return tuple(result)

    def _remove(self, elements: tuple[Element, ...], id: str) -> tuple[Element, ...]:
        return tuple(
            replace(element, elements=self._remove(element.elements, id))
            if isinstance(element, Container)
            else element
            for element in elements
            if element.id != id
        )

    def _walk(self, elements: tuple[Element, ...]) -> tuple[Element, ...]:
        result: list[Element] = []
        for element in elements:
            result.append(element)
            if isinstance(element, Container):
                result.extend(self._walk(element.elements))
        return tuple(result)
