from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

from ...core.element import Entity


class DomainKind(StrEnum):
    COMPLEX = "complex"
    COMPLICATED = "complicated"
    CLEAR = "clear"
    CHAOTIC = "chaotic"
    CONFUSION = "confusion"


@dataclass(frozen=True, slots=True)
class Domain(Entity):
    kind: ClassVar[str] = "domain"
    domain: DomainKind = DomainKind.COMPLEX
