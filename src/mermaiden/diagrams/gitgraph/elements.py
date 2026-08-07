from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Entity
from ..domain import DiagramElementMember


class GitGraphElementMember(DiagramElementMember):
    description: ClassVar[str] = "valid in Git Graph"


@dataclass(frozen=True, slots=True)
class Commit(Entity, GitGraphElementMember):
    kind: ClassVar[str] = "commit"
    commit_type: str = ""
    tag: str = ""


@dataclass(frozen=True, slots=True)
class Branch(Entity, GitGraphElementMember):
    kind: ClassVar[str] = "branch"
    order: float | None = None


@dataclass(frozen=True, slots=True)
class Checkout(Entity, GitGraphElementMember):
    kind: ClassVar[str] = "checkout"
