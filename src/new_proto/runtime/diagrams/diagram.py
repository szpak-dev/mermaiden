from dataclasses import dataclass

from ...core.annotation import Annotation
from ...core.constraint import Constraint
from ...core.diagram import Diagram, DiagramVisitor
from ...core.element import Element
from ...core.relation import Relation


@dataclass(frozen=True, slots=True)
class FrozenDiagram(Diagram):
    diagram_id: str
    element_values: tuple[Element, ...] = ()
    relation_values: tuple[Relation, ...] = ()
    annotation_values: tuple[Annotation, ...] = ()
    constraint_values: tuple[Constraint, ...] = ()

    @property
    def id(self) -> str:
        return self.diagram_id

    @property
    def elements(self) -> tuple[Element, ...]:
        return self.element_values

    @property
    def relations(self) -> tuple[Relation, ...]:
        return self.relation_values

    @property
    def annotations(self) -> tuple[Annotation, ...]:
        return self.annotation_values

    @property
    def constraints(self) -> tuple[DiagramVisitor[object], ...]:
        return self.constraint_values
