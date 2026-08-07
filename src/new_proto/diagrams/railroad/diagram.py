from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..base import DiagramModel
from .configuration import RailroadDiagramConfiguration
from .constraints.constraint import RailroadDiagramConstraint
from .elements import NonTerminal, Terminal
from .elements import Sequence as RailroadSequence


@injectable(as_type=DiagramModel, qualifier="railroad", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class RailroadDiagram(DiagramModel):
    constraints: Sequence[RailroadDiagramConstraint]
    configuration: RailroadDiagramConfiguration = field(default_factory=RailroadDiagramConfiguration, init=False)
    syntax: ClassVar[str] = "railroad-ebnf-beta"
    name: ClassVar[str] = "Railroad diagram"
    config_key: ClassVar[str] = "railroad"
    schema_definition: ClassVar[str] = "RailroadDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return {self.config_key: self.configuration.to_mermaid()}

    def add_rule(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add rule '{id}'", RailroadSequence(id, label))

    def add_terminal(self, id: str, label: str, rule_id: str) -> ChangeReport:
        return self._add_element(f"add terminal '{id}'", Terminal(id, label), rule_id)

    def add_non_terminal(self, id: str, label: str, rule_id: str) -> ChangeReport:
        return self._add_element(f"add non-terminal '{id}'", NonTerminal(id, label), rule_id)
