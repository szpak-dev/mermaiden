from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

from ...core.element import Entity
from ..domain import DiagramElementMember


class CynefinElementMember(DiagramElementMember):
    description: ClassVar[str] = "valid in Cynefin diagram"


class DomainKind(StrEnum):
    COMPLEX = "complex"
    COMPLICATED = "complicated"
    CLEAR = "clear"
    CHAOTIC = "chaotic"
    CONFUSION = "confusion"


@dataclass(frozen=True, slots=True)
class Domain(Entity, CynefinElementMember):
    kind: ClassVar[str] = "domain"
    domain: DomainKind = DomainKind.COMPLEX
