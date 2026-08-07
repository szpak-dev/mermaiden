from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ..base import DiagramModel
from .configuration import EventModelingDiagramConfiguration
from .constraints.constraint import EventModelingDiagramConstraint


@injectable(as_type=DiagramModel, qualifier="eventmodeling", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class EventModelingDiagram(DiagramModel):
    constraints: Sequence[EventModelingDiagramConstraint]
    configuration: EventModelingDiagramConfiguration = field(
        default_factory=EventModelingDiagramConfiguration,
        init=False,
    )
    syntax: ClassVar[str] = "eventModeling"
    name: ClassVar[str] = "Event Modeling diagram"
    config_key: ClassVar[str] = "eventmodeling"
    schema_definition: ClassVar[str] = "EventModelingDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return {self.config_key: self.configuration.to_mermaid()}
