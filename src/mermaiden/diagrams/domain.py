from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import ClassVar

from ..core.constraint import (
    BlockingConstraint,
    Constraint,
    ConstraintDiagram,
    ValidationReport,
    Violation,
)
from ..core.diagram import Diagram
from ..runtime.diagrams.aggregate import DiagramAggregate
from ..runtime.domain import ConstraintInspection
from .configuration import MermaidDiagramConfiguration


@dataclass(frozen=True, slots=True)
class DiagramObserver[ConstraintT: Constraint](ConstraintInspection):
    structure: ConstraintInspection
    constraints: Sequence[ConstraintT]

    def inspect(self, diagram: Diagram) -> ValidationReport:
        structural = self.structure.inspect(diagram)
        domain = tuple(violation for constraint in self.constraints for violation in diagram.accept(constraint))
        return ValidationReport((*structural.violations, *domain))


@dataclass(frozen=True, slots=True)
class DiagramMembers(BlockingConstraint):
    package: str

    @property
    def code(self) -> str:
        return f"{self.package.rsplit('.', maxsplit=1)[-1]}.member_type"


    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        issues = [
            self.violation(
                f"Element '{item.id}' does not belong to this diagram.",
                path=f"elements.{item.id}",
            )
            for item in diagram.walk_elements()
            if item.__class__.__module__ != f"{self.package}.elements"
        ]
        issues.extend(
            self.violation(
                f"Relation '{item.id}' does not belong to this diagram.",
                path=f"relations.{item.id}",
            )
            for item in diagram.find_relations()
            if item.__class__.__module__ != f"{self.package}.relations"
        )
        issues.extend(
            self.violation(
                f"Annotation '{item.id}' does not belong to this diagram.",
                path=f"annotations.{item.id}",
            )
            for item in diagram.find_annotations()
            if item.__class__.__module__ != f"{self.package}.annotations"
        )
        return tuple(issues)


@dataclass(frozen=True, slots=True)
class DiagramDefinition:
    syntax: str
    name: str
    config_key: str
    schema_definition: str


@dataclass(frozen=True, slots=True)
class DiagramModel(DiagramAggregate):
    definition: ClassVar[DiagramDefinition]
    structure: ConstraintInspection
    constraints: Sequence[Constraint]
    configuration: MermaidDiagramConfiguration

    @property
    def kind(self) -> str:
        return self.definition.syntax

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return self.configuration.document(self.definition.config_key).to_mermaid()

    @property
    def observer(self) -> DiagramObserver[Constraint]:
        members = DiagramMembers(type(self).__module__.removesuffix(".diagram"))
        return DiagramObserver(self.structure, (members, *self.constraints))
