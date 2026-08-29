import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Annotated, ClassVar, cast

from pydantic import Field

from ..core.constraint import (
    BlockingConstraint,
    ChangeReport,
    Constraint,
    ConstraintDiagram,
    ValidationReport,
    Violation,
)
from ..core.diagram import Diagram
from ..core.element import Container, RequiresChildren
from ..mutations.domain import MutationKernel
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
class DiagramConstraint(BlockingConstraint):
    @staticmethod
    def _snake_case(value: str) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower()

    @property
    def code(self) -> str:
        package = getattr(self, "package", type(self).__module__)
        return f"{package.rsplit('.', maxsplit=1)[-1]}.{self._snake_case(type(self).__name__)}"


@dataclass(frozen=True, slots=True)
class Members(DiagramConstraint):
    package: str

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
        issues.extend(
            self.violation(
                f"Element '{item.id}' must contain at least one child.",
                path=f"elements.{item.id}",
            )
            for item in diagram.walk_elements()
            if isinstance(item, RequiresChildren) and not cast(Container, item).elements
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
    mutations: MutationKernel

    def update_element(
        self,
        id: str,
        kind: str,
        changes: Mapping[str, object],
    ) -> ChangeReport:
        return self.mutations.update_element(self, id, kind, changes)

    def update_relation(
        self,
        id: str,
        kind: str,
        changes: Mapping[str, object],
    ) -> ChangeReport:
        return self.mutations.update_relation(self, id, kind, changes)

    def update_annotation(
        self,
        id: str,
        kind: str,
        changes: Mapping[str, object],
    ) -> ChangeReport:
        return self.mutations.update_annotation(self, id, kind, changes)

    def move_element(
        self,
        id: str,
        kind: str,
        parent_id: str,
        position: int | None,
    ) -> ChangeReport:
        return self.mutations.move_element(self, id, kind, parent_id, position)

    def reorder_elements(
        self,
        parent_id: str,
        element_ids: Annotated[
            Sequence[Annotated[str, Field(min_length=1)]],
            Field(json_schema_extra={"uniqueItems": True}),
        ],
    ) -> ChangeReport:
        return self.mutations.reorder_elements(self, parent_id, element_ids)

    def configure(self, configuration: MermaidDiagramConfiguration) -> None:
        expected = type(self.configuration)
        if type(configuration) is not expected:
            raise TypeError(
                f"Configuration for '{self.kind}' must be '{expected.__name__}', "
                f"received '{type(configuration).__name__}'."
            )
        object.__setattr__(self, "configuration", configuration)

    @property
    def kind(self) -> str:
        return self.definition.syntax

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return self.configuration.document(self.definition.config_key).to_mermaid()

    @property
    def observer(self) -> DiagramObserver[Constraint]:
        members = Members(type(self).__module__.removesuffix(".diagram"))
        return DiagramObserver(self.structure, (members, *self.constraints))
