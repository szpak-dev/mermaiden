from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import ClassVar

from ..core.constraint import Constraint, ConstraintDiagram, ConstraintLevel, ValidationReport, Violation
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


class DiagramMember:
    description: ClassVar[str]


class DiagramElementMember(DiagramMember):
    pass


class DiagramRelationMember(DiagramMember):
    pass


class DiagramAnnotationMember(DiagramMember):
    pass


@dataclass(frozen=True, slots=True)
class DiagramMembersConstraint(Constraint):
    member_code: str
    element_member_type: type[DiagramElementMember]
    relation_member_type: type[DiagramRelationMember]
    annotation_member_type: type[DiagramAnnotationMember]

    @property
    def code(self) -> str:
        return self.member_code

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        issues = [
            self.violation(
                f"Element '{item.id}' is not {self.element_member_type.description}.",
                path=f"elements.{item.id}",
            )
            for item in diagram.walk_elements()
            if not isinstance(item, self.element_member_type)
        ]
        issues.extend(
            self.violation(
                f"Relation '{item.id}' is not {self.relation_member_type.description}.",
                path=f"relations.{item.id}",
            )
            for item in diagram.find_relations()
            if not isinstance(item, self.relation_member_type)
        )
        issues.extend(
            self.violation(
                f"Annotation '{item.id}' is not {self.annotation_member_type.description}.",
                path=f"annotations.{item.id}",
            )
            for item in diagram.find_annotations()
            if not isinstance(item, self.annotation_member_type)
        )
        return tuple(issues)


@dataclass(frozen=True, slots=True)
class DiagramMembers:
    code: str
    element_member_type: type[DiagramElementMember]
    relation_member_type: type[DiagramRelationMember]
    annotation_member_type: type[DiagramAnnotationMember]

    @property
    def constraint(self) -> DiagramMembersConstraint:
        return DiagramMembersConstraint(
            self.code,
            self.element_member_type,
            self.relation_member_type,
            self.annotation_member_type,
        )


@dataclass(frozen=True, slots=True)
class DiagramDefinition:
    syntax: str
    name: str
    config_key: str
    schema_definition: str


@dataclass(frozen=True, slots=True)
class DiagramModel(DiagramAggregate):
    definition: ClassVar[DiagramDefinition]
    members: ClassVar[DiagramMembers]
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
        return DiagramObserver(self.structure, (self.members.constraint, *self.constraints))
