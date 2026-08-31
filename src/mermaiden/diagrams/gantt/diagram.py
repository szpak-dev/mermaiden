from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.domain import ChangeReport
from ..domain import DiagramDefinition, DiagramModel
from .configuration import GanttConfiguration
from .constraints import GanttConstraint
from .elements import Marker, Milestone, Section, Task


@injectable(as_type=DiagramModel, qualifier="gantt", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Gantt(DiagramModel):
    constraints: Sequence[GanttConstraint]
    configuration: GanttConfiguration = field(default_factory=GanttConfiguration, init=False)
    title: str = field(default="", init=False)
    date_format: str = field(default="YYYY-MM-DD", init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "gantt",
        "Gantt chart",
        "gantt",
        "GanttDiagramConfig",
    )

    def set_title(self, title: str) -> None:
        object.__setattr__(self, "title", title)

    def set_date_format(self, date_format: str) -> None:
        object.__setattr__(self, "date_format", date_format)

    def add_section(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add section '{id}'", Section(id=id, label=label))

    def add_task(self, id: str, label: str, metadata: tuple[str, ...], section_id: str) -> ChangeReport:
        return self._add_element(f"add task '{id}'", Task(id=id, label=label, metadata=metadata), section_id)

    def add_milestone(self, id: str, label: str, metadata: tuple[str, ...], section_id: str) -> ChangeReport:
        return self._add_element(
            f"add milestone '{id}'", Milestone(id=id, label=label, metadata=("milestone", *metadata)), section_id
        )

    def add_marker(self, id: str, label: str, date: str) -> ChangeReport:
        return self._add_element(f"add marker '{id}'", Marker(id=id, label=label, date=date))
