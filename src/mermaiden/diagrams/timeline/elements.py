from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity


@dataclass(frozen=True, slots=True)
class TimelineSection(Container):
    kind: ClassVar[str] = "timeline_section"


@dataclass(frozen=True, slots=True)
class TimelinePeriod(Container):
    kind: ClassVar[str] = "timeline_period"


@dataclass(frozen=True, slots=True)
class TimelineEvent(Entity):
    kind: ClassVar[str] = "timeline_event"
