from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramModel
from .configuration import VennConfiguration
from .constraints.constraint import VennConstraint
from .elements import VennSet, VennText, VennUnion


@injectable(as_type=DiagramModel, qualifier="venn", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Venn(DiagramModel):
    constraints: Sequence[VennConstraint]
    configuration: VennConfiguration = field(default_factory=VennConfiguration, init=False)
    syntax: ClassVar[str] = "venn-beta"
    name: ClassVar[str] = "Venn diagram"
    config_key: ClassVar[str] = "venn"
    schema_definition: ClassVar[str] = "VennDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return {self.config_key: self.configuration.to_mermaid()}

    def add_set(self, id: str, label: str, size: float | None = None) -> ChangeReport:
        return self._add_element(f"add set '{id}'", VennSet(id, label, (), size))

    def add_union(
        self,
        id: str,
        label: str,
        set_ids: tuple[str, ...],
        size: float | None = None,
    ) -> ChangeReport:
        return self._add_element(f"add union '{id}'", VennUnion(id, label, (), set_ids, size))

    def add_text(self, id: str, label: str, parent_id: str) -> ChangeReport:
        return self._add_element(f"add text '{id}'", VennText(id, label), parent_id)
