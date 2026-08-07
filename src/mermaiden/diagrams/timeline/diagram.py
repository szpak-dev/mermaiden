from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramDefinition, DiagramMembers, DiagramModel
from .configuration import TimelineDiagramConfiguration
from .constraints import TimelineAnnotationMember, TimelineConstraint, TimelineRelationMember
from .elements import TimelineElementMember, TimelineEvent, TimelinePeriod, TimelineSection


@injectable(as_type=DiagramModel, qualifier="timeline", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Timeline(DiagramModel):
    constraints: Sequence[TimelineConstraint]
    members: ClassVar[DiagramMembers] = DiagramMembers(
        "timeline.member_type",
        TimelineElementMember,
        TimelineRelationMember,
        TimelineAnnotationMember,
    )
    configuration: TimelineDiagramConfiguration = field(default_factory=TimelineDiagramConfiguration, init=False)
    title: str = field(default="", init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "timeline",
        "Timeline",
        "timeline",
        "TimelineDiagramConfig",
    )


    def set_title(self, title: str) -> None:
        object.__setattr__(self, "title", title)

    def add_section(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add section '{id}'", TimelineSection(id, label))

    def add_period(self, id: str, label: str, section_id: str = "") -> ChangeReport:
        return self._add_element(f"add period '{id}'", TimelinePeriod(id, label), section_id)

    def add_event(self, id: str, label: str, period_id: str) -> ChangeReport:
        return self._add_element(f"add event '{id}'", TimelineEvent(id, label), period_id)
