from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Entity


@dataclass(frozen=True, slots=True)
class Commit(Entity):
    kind: ClassVar[str] = "commit"
    commit_type: str = ""
    tag: str = ""


@dataclass(frozen=True, slots=True)
class Branch(Entity):
    kind: ClassVar[str] = "branch"
    order: float | None = None


@dataclass(frozen=True, slots=True)
class Checkout(Entity):
    kind: ClassVar[str] = "checkout"
