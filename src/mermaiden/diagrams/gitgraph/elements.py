from enum import StrEnum

from ...core.element import Entity


class CommitType(StrEnum):
    NORMAL = "NORMAL"
    REVERSE = "REVERSE"
    HIGHLIGHT = "HIGHLIGHT"


class Commit(Entity):
    commit_type: CommitType | str = ""
    tag: str = ""


class Branch(Entity):
    order: int | None = None


class Checkout(Entity):
    pass
