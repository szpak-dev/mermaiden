from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramModel
from .configuration import EventModelingDiagramConfiguration
from .constraints import EventModelingDiagramConstraint
from .elements import Actor, Command, Event, Swimlane, View
from .relations import Flow


@injectable(as_type=DiagramModel, qualifier="eventmodeling", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class EventModelingDiagram(DiagramModel):
    constraints: Sequence[EventModelingDiagramConstraint]
    configuration: EventModelingDiagramConfiguration = field(
        default_factory=EventModelingDiagramConfiguration,
        init=False,
    )
    syntax: ClassVar[str] = "eventmodeling"
    name: ClassVar[str] = "Event Modeling diagram"
    config_key: ClassVar[str] = "eventmodeling"
    schema_definition: ClassVar[str] = "EventModelingDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return self.configuration.document(self.config_key).to_mermaid()

    def add_swimlane(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add swimlane '{id}'", Swimlane(id, label))

    def add_actor(self, id: str, label: str, swimlane_id: str) -> ChangeReport:
        return self._add_element(f"add actor '{id}'", Actor(id, label), swimlane_id)

    def add_command(self, id: str, label: str, swimlane_id: str) -> ChangeReport:
        return self._add_element(f"add command '{id}'", Command(id, label), swimlane_id)

    def add_view(self, id: str, label: str, swimlane_id: str) -> ChangeReport:
        return self._add_element(f"add view '{id}'", View(id, label), swimlane_id)

    def add_event(self, id: str, label: str, swimlane_id: str) -> ChangeReport:
        return self._add_element(f"add event '{id}'", Event(id, label), swimlane_id)

    def add_flow(self, id: str, source_id: str, target_id: str) -> ChangeReport:
        return self._add_relation(f"add flow '{id}'", Flow(id, (source_id, target_id)))
