from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramDefinition, DiagramModel
from .configuration import VennConfiguration
from .constraints import VennConstraint
from .elements import VennSet, VennText, VennUnion


@injectable(as_type=DiagramModel, qualifier="venn", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Venn(DiagramModel):
    constraints: Sequence[VennConstraint]
    configuration: VennConfiguration = field(default_factory=VennConfiguration, init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "venn-beta",
        "Venn diagram",
        "venn",
        "VennDiagramConfig",
    )


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
