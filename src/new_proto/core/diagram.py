from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import Protocol, TypeVar

from .annotation import Annotation
from .constraint import ChangeReport, ValidationReport
from .element import Container, Element, Entity
from .relation import Relation

Result = TypeVar("Result", covariant=True)


class DiagramVisitor(Protocol[Result]):
    def visit(self, diagram: "Diagram") -> Result: ...


class Diagram(ABC):
    """State-owning aggregate and the only authority over its building blocks.

    A new diagram is empty and ready for incremental construction. Operations
    may leave it semantically incomplete, but must never commit structurally
    corrupt state.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """Stable diagram-kind identifier, for example ``flowchart``."""

    @abstractmethod
    def add_container(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        """Add an empty container at the root or inside another container."""

    @abstractmethod
    def add_entity(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        """Add an entity at the root or inside an existing container."""

    @abstractmethod
    def connect(
        self,
        id: str,
        element_ids: Sequence[str],
        label: str,
    ) -> ChangeReport:
        """Bind at least two existing elements with a relation."""

    @abstractmethod
    def annotate(
        self,
        id: str,
        data: Mapping[str, object],
        element_ids: Sequence[str] = (),
        relation_ids: Sequence[str] = (),
    ) -> ChangeReport:
        """Attach non-structural data to existing elements or relations."""

    @abstractmethod
    def remove_element(self, id: str, *, cascade: bool = False) -> ChangeReport:
        """Remove an element, rejecting dependent state unless cascade is explicit."""

    @abstractmethod
    def remove_relation(self, id: str) -> ChangeReport:
        """Remove a relation by its diagram-local ID."""

    @abstractmethod
    def remove_annotation(self, id: str) -> ChangeReport:
        """Remove an annotation by its diagram-local ID."""

    @abstractmethod
    def find_element(self, id: str) -> Element | None:
        """Look up one element anywhere in the containment tree."""

    @abstractmethod
    def walk_elements(self, parent_id: str = "") -> Sequence[Element]:
        """Traverse every element at the root or below one container."""

    @abstractmethod
    def find_relations(self, element_id: str = "") -> Sequence[Relation]:
        """Return every relation or only relations containing one element."""

    @abstractmethod
    def find_annotations(self, target_id: str = "") -> Sequence[Annotation]:
        """Return every annotation or only annotations for one target."""

    @abstractmethod
    def validate(self) -> ValidationReport:
        """Inspect the current, possibly incomplete, diagram state."""

    def accept(self, visitor: DiagramVisitor[Result]) -> Result:
        return visitor.visit(self)


__all__ = ["Container", "Diagram", "DiagramVisitor", "Element", "Entity", "Relation"]
