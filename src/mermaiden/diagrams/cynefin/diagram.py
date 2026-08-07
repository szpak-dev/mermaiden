from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramModel
from .configuration import CynefinDiagramConfiguration
from .constraints.constraint import CynefinDiagramConstraint
from .elements import Domain, DomainKind
from .relations import Transition


@injectable(as_type=DiagramModel, qualifier="cynefin", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class CynefinDiagram(DiagramModel):
    constraints: Sequence[CynefinDiagramConstraint]
    configuration: CynefinDiagramConfiguration = field(default_factory=CynefinDiagramConfiguration, init=False)
    syntax: ClassVar[str] = "cynefin-beta"
    name: ClassVar[str] = "Cynefin diagram"
    config_key: ClassVar[str] = "cynefin"
    schema_definition: ClassVar[str] = "CynefinDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return {self.config_key: self.configuration.to_mermaid()}

    def add_item(self, id: str, label: str, domain: DomainKind) -> ChangeReport:
        return self._add_element(f"add {domain.value} item '{id}'", Domain(id, label, domain))

    def add_transition(self, id: str, source_id: str, target_id: str, label: str = "") -> ChangeReport:
        return self._add_relation(f"add transition '{id}'", Transition(id, (source_id, target_id), label))
