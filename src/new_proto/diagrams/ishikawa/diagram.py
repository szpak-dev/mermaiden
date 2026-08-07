from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ..base import DiagramModel
from .configuration import IshikawaDiagramConfiguration
from .constraints.constraint import IshikawaDiagramConstraint


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
