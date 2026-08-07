from typing import ClassVar

from wireup import injectable

from ...base import DiagramMembersConstraint
from ..elements import Branch, Checkout, Commit
from ..relations import CommitRelation
from .constraint import GitGraphDiagramConstraint


@injectable(as_type=GitGraphDiagramConstraint, qualifier="gitgraph_members")
class GitGraphDiagramMembers(DiagramMembersConstraint, GitGraphDiagramConstraint):
    element_types: ClassVar = (Commit, Branch, Checkout)
    relation_types: ClassVar = (CommitRelation,)
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in Git Graph"
    relation_description: ClassVar[str] = "valid in Git Graph"
    annotation_description: ClassVar[str] = "valid in Git Graph"

    @property
    def code(self) -> str:
        return "gitgraph.member_type"
