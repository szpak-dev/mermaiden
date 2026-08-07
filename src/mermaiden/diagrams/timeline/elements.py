from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity
from ..domain import DiagramElementMember


class TimelineElementMember(DiagramElementMember):
    description: ClassVar[str] = "valid in a timeline"


@dataclass(frozen=True, slots=True)
class TimelineSection(Container, TimelineElementMember):
    kind: ClassVar[str] = "timeline_section"


@dataclass(frozen=True, slots=True)
class TimelinePeriod(Container, TimelineElementMember):
    kind: ClassVar[str] = "timeline_period"


@dataclass(frozen=True, slots=True)
class TimelineEvent(Entity, TimelineElementMember):
    kind: ClassVar[str] = "timeline_event"
