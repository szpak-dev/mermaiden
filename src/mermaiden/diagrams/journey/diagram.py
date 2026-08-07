from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramModel
from .configuration import JourneyDiagramConfiguration
from .constraints import JourneyConstraint
from .elements import JourneySection, JourneyTask


@injectable(as_type=DiagramModel, qualifier="journey", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Journey(DiagramModel):
    constraints: Sequence[JourneyConstraint]
    configuration: JourneyDiagramConfiguration = field(default_factory=JourneyDiagramConfiguration, init=False)
    title: str = field(default="", init=False)
    syntax: ClassVar[str] = "journey"
    name: ClassVar[str] = "User journey"
    config_key: ClassVar[str] = "journey"
    schema_definition: ClassVar[str] = "JourneyDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return self.configuration.document(self.config_key).to_mermaid()

    def set_title(self, title: str) -> None:
        object.__setattr__(self, "title", title)

    def add_section(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add section '{id}'", JourneySection(id, label))

    def add_task(self, id: str, label: str, score: int, actors: tuple[str, ...], section_id: str) -> ChangeReport:
        return self._add_element(f"add task '{id}'", JourneyTask(id, label, score, actors), section_id)
