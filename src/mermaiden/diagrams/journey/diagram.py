from abc import ABC
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport, Constraint, ConstraintDiagram, Violation
from ..base import DiagramMembersConstraint, DiagramModel
from .elements import JourneySection, JourneyTask


class JourneyConstraint(Constraint, ABC):
    pass


@injectable(as_type=JourneyConstraint, qualifier="journey_structure")
class JourneyStructure(JourneyConstraint):
    @property
    def code(self) -> str:
        return "journey.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()


@injectable(as_type=JourneyConstraint, qualifier="journey_members")
class JourneyMembers(DiagramMembersConstraint, JourneyConstraint):
    element_types: ClassVar = (JourneySection, JourneyTask)
    relation_types: ClassVar = ()
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in a user journey"
    relation_description: ClassVar[str] = "valid in a user journey"
    annotation_description: ClassVar[str] = "valid in a user journey"

    @property
    def code(self) -> str:
        return "journey.member_type"


@injectable(as_type=DiagramModel, qualifier="journey", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Journey(DiagramModel):
    constraints: Sequence[JourneyConstraint]
    title: str = field(default="", init=False)
    syntax: ClassVar[str] = "journey"
    name: ClassVar[str] = "User journey"
    config_key: ClassVar[str] = "journey"
    schema_definition: ClassVar[str] = "JourneyDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return {}

    def set_title(self, title: str) -> None:
        object.__setattr__(self, "title", title)

    def add_section(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add section '{id}'", JourneySection(id, label))

    def add_task(self, id: str, label: str, score: int, actors: tuple[str, ...], section_id: str) -> ChangeReport:
        return self._add_element(f"add task '{id}'", JourneyTask(id, label, score, actors), section_id)
