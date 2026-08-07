from dataclasses import dataclass
from typing import ClassVar

from ...core.relation import Relation
from ..domain import DiagramRelationMember


class GitGraphRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "valid in Git Graph"


@dataclass(frozen=True, slots=True)
class CommitRelation(Relation, GitGraphRelationMember):
    kind: ClassVar[str] = "commitrelation"

