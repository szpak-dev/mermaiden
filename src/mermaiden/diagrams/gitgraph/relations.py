from dataclasses import dataclass
from typing import ClassVar

from ...core.relation import Relation


@dataclass(frozen=True, slots=True)
class CommitRelation(Relation):
    kind: ClassVar[str] = "commitrelation"

