from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar

from ..core.annotation import Annotation
from ..core.constraint import Constraint, ConstraintDiagram, ConstraintLevel, ValidationReport, Violation
from ..core.diagram import Diagram
from ..core.element import Element
from ..core.relation import Relation
from ..runtime.diagrams.aggregate import DiagramAggregate
from ..runtime.domain import ConstraintInspection


@dataclass(frozen=True, slots=True)
class DiagramObserver[ConstraintT: Constraint](ConstraintInspection):
    structure: ConstraintInspection
    constraints: Sequence[ConstraintT]

    def inspect(self, diagram: Diagram) -> ValidationReport:
        structural = self.structure.inspect(diagram)
        domain = tuple(violation for constraint in self.constraints for violation in diagram.accept(constraint))
        return ValidationReport((*structural.violations, *domain))


class DiagramMembersConstraint(Constraint):
    element_types: ClassVar[tuple[type[Element], ...]]
    relation_types: ClassVar[tuple[type[Relation], ...]]
    annotation_types: ClassVar[tuple[type[Annotation], ...]]
    element_description: ClassVar[str]
    relation_description: ClassVar[str]
    annotation_description: ClassVar[str]

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        issues = [
            self.violation(f"Element '{item.id}' is not {self.element_description}.", path=f"elements.{item.id}")
            for item in diagram.walk_elements()
            if not isinstance(item, self.element_types)
        ]
        issues.extend(
            self.violation(f"Relation '{item.id}' is not {self.relation_description}.", path=f"relations.{item.id}")
            for item in diagram.find_relations()
            if not isinstance(item, self.relation_types)
        )
        issues.extend(
            self.violation(
                f"Annotation '{item.id}' is not {self.annotation_description}.",
                path=f"annotations.{item.id}",
            )
            for item in diagram.find_annotations()
            if not isinstance(item, self.annotation_types)
        )
        return tuple(issues)


@dataclass(frozen=True, slots=True)
class DiagramModel(DiagramAggregate):
    syntax: ClassVar[str]
    name: ClassVar[str]
    config_key: ClassVar[str]
    schema_definition: ClassVar[str]
    structure: ConstraintInspection
    constraints: Sequence[Constraint]

    @property
    def kind(self) -> str:
        return self.syntax

    @property
    def observer(self) -> DiagramObserver[Constraint]:
        return DiagramObserver(self.structure, self.constraints)
