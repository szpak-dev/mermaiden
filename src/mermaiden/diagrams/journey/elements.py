from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity
from ..domain import DiagramElementMember


class JourneyElementMember(DiagramElementMember):
    description: ClassVar[str] = "valid in a user journey"


@dataclass(frozen=True, slots=True)
class JourneySection(Container, JourneyElementMember):
    kind: ClassVar[str] = "journey_section"


@dataclass(frozen=True, slots=True)
class JourneyTask(Entity, JourneyElementMember):
    kind: ClassVar[str] = "journey_task"
    score: int = 1
    actors: tuple[str, ...] = ()
