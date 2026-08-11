from enum import StrEnum

from ...core.element import Entity


class DomainKind(StrEnum):
    COMPLEX = "complex"
    COMPLICATED = "complicated"
    CLEAR = "clear"
    CHAOTIC = "chaotic"
    CONFUSION = "confusion"


class Domain(Entity):
    domain: DomainKind = DomainKind.COMPLEX
