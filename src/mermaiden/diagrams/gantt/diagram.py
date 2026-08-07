from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramModel
from .configuration import GanttConfiguration
from .constraints.constraint import GanttConstraint
from .elements import Marker, Milestone, Section, Task


@injectable(as_type=DiagramModel, qualifier="gantt", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Gantt(DiagramModel):
    constraints: Sequence[GanttConstraint]
    configuration: GanttConfiguration = field(default_factory=GanttConfiguration, init=False)
    title: str = field(default="", init=False)
    date_format: str = field(default="YYYY-MM-DD", init=False)
    syntax: ClassVar[str] = "gantt"
    name: ClassVar[str] = "Gantt chart"
    config_key: ClassVar[str] = "gantt"
    schema_definition: ClassVar[str] = "GanttDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return self.configuration.document(self.config_key).to_mermaid()

    def set_title(self, title: str) -> None:
        object.__setattr__(self, "title", title)

    def set_date_format(self, date_format: str) -> None:
        object.__setattr__(self, "date_format", date_format)

    def add_section(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add section '{id}'", Section(id, label))

    def add_task(self, id: str, label: str, metadata: tuple[str, ...], section_id: str) -> ChangeReport:
        return self._add_element(f"add task '{id}'", Task(id, label, metadata), section_id)

    def add_milestone(self, id: str, label: str, metadata: tuple[str, ...], section_id: str) -> ChangeReport:
        return self._add_element(f"add milestone '{id}'", Milestone(id, label, ("milestone", *metadata)), section_id)

    def add_marker(self, id: str, label: str, date: str) -> ChangeReport:
        return self._add_element(f"add marker '{id}'", Marker(id, label, date))
