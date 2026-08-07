from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramModel
from .configuration import BlockDiagramConfiguration
from .constraints import BlockDiagramConstraint
from .elements import BlockGroup, BlockNode, BlockSpace


@injectable(as_type=DiagramModel, qualifier="block", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class BlockDiagram(DiagramModel):
    constraints: Sequence[BlockDiagramConstraint]
    configuration: BlockDiagramConfiguration = field(default_factory=BlockDiagramConfiguration, init=False)
    columns: int | None = field(default=None, init=False)
    syntax: ClassVar[str] = "block"
    name: ClassVar[str] = "Block diagram"
    config_key: ClassVar[str] = "block"
    schema_definition: ClassVar[str] = "BlockDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return self.configuration.document(self.config_key).to_mermaid()

    def set_columns(self, columns: int) -> None:
        object.__setattr__(self, "columns", columns)

    def add_group(self, id: str, label: str, columns: int | None = None, span: int | None = None) -> ChangeReport:
        return self._add_element(f"add group '{id}'", BlockGroup(id, label, (), columns, span))

    def add_block(self, id: str, label: str, span: int | None = None, parent_id: str = "") -> ChangeReport:
        return self._add_element(f"add block '{id}'", BlockNode(id, label, span), parent_id)

    def add_space(self, id: str, span: int | None = None, parent_id: str = "") -> ChangeReport:
        return self._add_element(f"add space '{id}'", BlockSpace(id, "space", span), parent_id)
