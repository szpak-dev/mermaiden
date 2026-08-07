from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramModel
from .configuration import PieDiagramConfiguration
from .constraints import PieConstraint
from .elements import PieSlice


@injectable(as_type=DiagramModel, qualifier="pie", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class PieDiagram(DiagramModel):
    constraints: Sequence[PieConstraint]
    configuration: PieDiagramConfiguration = field(default_factory=PieDiagramConfiguration, init=False)
    title: str = field(default="", init=False)
    show_data: bool = field(default=False, init=False)
    syntax: ClassVar[str] = "pie"
    name: ClassVar[str] = "Pie chart"
    config_key: ClassVar[str] = "pie"
    schema_definition: ClassVar[str] = "PieDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return self.configuration.document(self.config_key).to_mermaid()

    def set_title(self, title: str) -> None:
        object.__setattr__(self, "title", title)

    def show_values(self) -> None:
        object.__setattr__(self, "show_data", True)

    def add_slice(self, id: str, label: str, value: float) -> ChangeReport:
        return self._add_element(f"add pie slice '{id}'", PieSlice(id, label, value))
