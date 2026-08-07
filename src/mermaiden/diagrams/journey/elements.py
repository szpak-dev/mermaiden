from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity


@dataclass(frozen=True, slots=True)
class JourneySection(Container):
    kind: ClassVar[str] = "journey_section"


@dataclass(frozen=True, slots=True)
class JourneyTask(Entity):
    kind: ClassVar[str] = "journey_task"
    score: int = 1
    actors: tuple[str, ...] = ()
