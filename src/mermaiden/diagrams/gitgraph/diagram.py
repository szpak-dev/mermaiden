from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramDefinition, DiagramMembers, DiagramModel
from .configuration import GitGraphDiagramConfiguration
from .constraints import GitGraphAnnotationMember, GitGraphDiagramConstraint
from .elements import Branch, Checkout, Commit, GitGraphElementMember
from .relations import GitGraphRelationMember


@injectable(as_type=DiagramModel, qualifier="gitgraph", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class GitGraphDiagram(DiagramModel):
    constraints: Sequence[GitGraphDiagramConstraint]
    members: ClassVar[DiagramMembers] = DiagramMembers(
        "gitgraph.member_type",
        GitGraphElementMember,
        GitGraphRelationMember,
        GitGraphAnnotationMember,
    )
    configuration: GitGraphDiagramConfiguration = field(default_factory=GitGraphDiagramConfiguration, init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "gitGraph",
        "Git Graph",
        "gitGraph",
        "GitGraphDiagramConfig",
    )


    def add_commit(self, id: str, label: str, commit_type: str = "", tag: str = "") -> ChangeReport:
        return self._add_element(f"add commit '{id}'", Commit(id, label, commit_type, tag))

    def add_branch(self, id: str, label: str, order: float | None = None) -> ChangeReport:
        return self._add_element(f"add branch '{id}'", Branch(id, label, order))

    def checkout(self, id: str, branch: str) -> ChangeReport:
        return self._add_element(f"checkout branch '{branch}'", Checkout(id, branch))
