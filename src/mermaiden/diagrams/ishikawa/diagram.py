from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..base import DiagramModel
from .configuration import IshikawaDiagramConfiguration
from .constraints.constraint import IshikawaDiagramConstraint
from .elements import Category, Cause, Effect


@injectable(as_type=DiagramModel, qualifier="ishikawa", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class IshikawaDiagram(DiagramModel):
    constraints: Sequence[IshikawaDiagramConstraint]
    configuration: IshikawaDiagramConfiguration = field(default_factory=IshikawaDiagramConfiguration, init=False)
    syntax: ClassVar[str] = "ishikawa-beta"
    name: ClassVar[str] = "Ishikawa diagram"
    config_key: ClassVar[str] = "ishikawa"
    schema_definition: ClassVar[str] = "IshikawaDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return {self.config_key: self.configuration.to_mermaid()}

    def add_effect(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add effect '{id}'", Effect(id, label))

    def add_category(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self._add_element(f"add category '{id}'", Category(id, label), parent_id)

    def add_cause(self, id: str, label: str, parent_id: str) -> ChangeReport:
        return self._add_element(f"add cause '{id}'", Cause(id, label), parent_id)
