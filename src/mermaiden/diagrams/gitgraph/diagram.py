from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramModel
from .configuration import GitGraphDiagramConfiguration
from .constraints.constraint import GitGraphDiagramConstraint
from .elements import Branch, Checkout, Commit


@injectable(as_type=DiagramModel, qualifier="gitgraph", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class GitGraphDiagram(DiagramModel):
    constraints: Sequence[GitGraphDiagramConstraint]
    configuration: GitGraphDiagramConfiguration = field(default_factory=GitGraphDiagramConfiguration, init=False)
    syntax: ClassVar[str] = "gitGraph"
    name: ClassVar[str] = "Git Graph"
    config_key: ClassVar[str] = "gitGraph"
    schema_definition: ClassVar[str] = "GitGraphDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return self.configuration.document(self.config_key).to_mermaid()

    def add_commit(self, id: str, label: str, commit_type: str = "", tag: str = "") -> ChangeReport:
        return self._add_element(f"add commit '{id}'", Commit(id, label, commit_type, tag))

    def add_branch(self, id: str, label: str, order: float | None = None) -> ChangeReport:
        return self._add_element(f"add branch '{id}'", Branch(id, label, order))

    def checkout(self, id: str, branch: str) -> ChangeReport:
        return self._add_element(f"checkout branch '{branch}'", Checkout(id, branch))
