from dataclasses import dataclass, field

from ..core.diagram import Diagram, DiagramContents
from ..core.element import Container, Element
from ..core.relation import Relation
from .elements import ManagedContainer


@dataclass(frozen=True)
class InMemoryDiagram(Diagram):
    _elements: dict[str, Element] = field(init=False, default_factory=dict[str, Element])
    _relations: list[Relation] = field(init=False, default_factory=list[Relation])

    def contents(self) -> DiagramContents:
        return DiagramSnapshot(tuple(self._elements.values()), tuple(self._relations))

    def add_element(self, element: Element, *, owner: Container | None = None) -> None:
        if element.id in self._elements:
            raise ValueError(f"Element '{element.id}' is already registered.")
        if isinstance(element, Container) and not isinstance(element, ManagedContainer):
            raise TypeError("Container must be managed by this diagram runtime.")
        if owner is not None:
            if not self._contains_element(owner):
                raise ValueError("Element owner does not belong to this diagram.")
            if not isinstance(owner, ManagedContainer):
                raise TypeError("Element owner must be managed by this diagram runtime.")
        self._elements[element.id] = element
        if owner is not None:
            owner.attach(element)

    def remove_element(self, element: Element) -> None:
        if not self._contains_element(element):
            raise ValueError("Element does not belong to this diagram.")
        removed = self._subtree(element)
        self._detach_from_owner(element)
        for current in removed:
            if isinstance(current, ManagedContainer):
                for child in current.children:
                    current.detach(child)
        for current in removed:
            self._elements.pop(current.id)
        self._relations[:] = [
            relation
            for relation in self._relations
            if not any(self._contains(removed, participant) for participant in relation.participants)
        ]

    def add_relation(self, relation: Relation) -> None:
        if not all(self._contains_element(participant) for participant in relation.participants):
            raise ValueError("Relation participants must belong to this diagram.")
        self._relations.append(relation)

    def remove_relation(self, relation: Relation) -> None:
        if not self._contains_relation(relation):
            raise ValueError("Relation does not belong to this diagram.")
        self._relations[:] = [candidate for candidate in self._relations if candidate is not relation]

    def _contains_element(self, element: Element) -> bool:
        return self._elements.get(element.id) is element

    def _resolve_element(self, id: str) -> Element:
        return self._elements[id]

    def _contains_relation(self, relation: Relation) -> bool:
        return self._contains(self._relations, relation)

    def _detach_from_owner(self, element: Element) -> None:
        for candidate in self._elements.values():
            if isinstance(candidate, ManagedContainer) and self._contains(candidate.children, element):
                candidate.detach(element)
                return

    def _subtree(self, element: Element) -> tuple[Element, ...]:
        descendants: list[Element] = [element]
        if isinstance(element, ManagedContainer):
            for child in element.children:
                descendants.extend(self._subtree(child))
        return tuple(descendants)

    @staticmethod
    def _contains(items: tuple[Element, ...] | list[Element] | list[Relation], item: object) -> bool:
        return any(candidate is item for candidate in items)


class DiagramSnapshot(DiagramContents):
    def __init__(self, elements: tuple[Element, ...], relations: tuple[Relation, ...]):
        self._elements = elements
        self._relations = relations

    @property
    def elements(self) -> tuple[Element, ...]:
        return self._elements

    @property
    def relations(self) -> tuple[Relation, ...]:
        return self._relations
