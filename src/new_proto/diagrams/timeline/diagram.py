from abc import ABC
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport, Constraint, ConstraintDiagram, Violation
from ..base import DiagramModel
from .elements import TimelineEvent, TimelinePeriod, TimelineSection


class TimelineConstraint(Constraint, ABC):
    pass


@injectable(as_type=TimelineConstraint, qualifier="timeline_structure")
class TimelineStructure(TimelineConstraint):
    @property
    def code(self) -> str:
        return "timeline.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()


@injectable(as_type=DiagramModel, qualifier="timeline", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Timeline(DiagramModel):
    constraints: Sequence[TimelineConstraint]
    title: str = field(default="", init=False)
    syntax: ClassVar[str] = "timeline"
    name: ClassVar[str] = "Timeline"
    config_key: ClassVar[str] = "timeline"
    schema_definition: ClassVar[str] = "TimelineDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return {}

    def set_title(self, title: str) -> None:
        object.__setattr__(self, "title", title)

    def add_section(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add section '{id}'", TimelineSection(id, label))

    def add_period(self, id: str, label: str, section_id: str = "") -> ChangeReport:
        return self._add_element(f"add period '{id}'", TimelinePeriod(id, label), section_id)

    def add_event(self, id: str, label: str, period_id: str) -> ChangeReport:
        return self._add_element(f"add event '{id}'", TimelineEvent(id, label), period_id)
