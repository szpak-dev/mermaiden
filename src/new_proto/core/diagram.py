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


class DiagramView(ABC):
    @property
    @abstractmethod
    def kind(self) -> str:
        ...

    @property
    @abstractmethod
    def root_elements(self) -> Sequence[Element]:
        ...

    @abstractmethod
    def find_element(self, id: str) -> Element | None:
        ...

    @abstractmethod
    def walk_elements(self, parent_id: str = "") -> Sequence[Element]:
        ...

    @abstractmethod
    def find_relations(self, element_id: str = "") -> Sequence[Relation]:
        ...

    @abstractmethod
    def find_annotations(self, target_id: str = "") -> Sequence[Annotation]:
        ...

    @abstractmethod
    def validate(self) -> ValidationReport:
        ...


class Diagram(DiagramView):
    @abstractmethod
    def add_container(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        ...

    @abstractmethod
    def add_entity(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        ...

    @abstractmethod
    def connect(
        self,
        id: str,
        element_ids: Sequence[str],
        label: str = "",
    ) -> ChangeReport:
        ...

    @abstractmethod
    def annotate(
        self,
        id: str,
        data: Mapping[str, object],
        element_ids: Sequence[str] = (),
        relation_ids: Sequence[str] = (),
    ) -> ChangeReport:
        ...

    @abstractmethod
    def remove_element(self, id: str, *, cascade: bool = False) -> ChangeReport:
        ...

    @abstractmethod
    def remove_relation(self, id: str) -> ChangeReport:
        ...

    @abstractmethod
    def remove_annotation(self, id: str) -> ChangeReport:
        ...

    def accept(self, visitor: DiagramVisitor[Result]) -> Result:
        return visitor.visit(self)


__all__ = [
    "Container",
    "Diagram",
    "DiagramView",
    "DiagramVisitor",
    "Element",
    "Entity",
    "Relation",
]
