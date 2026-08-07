from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramDefinition, DiagramModel
from .configuration import IshikawaDiagramConfiguration
from .constraints import IshikawaDiagramConstraint
from .elements import Category, Cause, Effect


@injectable(as_type=DiagramModel, qualifier="ishikawa", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class IshikawaDiagram(DiagramModel):
    constraints: Sequence[IshikawaDiagramConstraint]
    configuration: IshikawaDiagramConfiguration = field(default_factory=IshikawaDiagramConfiguration, init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "ishikawa-beta",
        "Ishikawa diagram",
        "ishikawa",
        "IshikawaDiagramConfig",
    )


    def add_effect(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add effect '{id}'", Effect(id, label))

    def add_category(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self._add_element(f"add category '{id}'", Category(id, label), parent_id)

    def add_cause(self, id: str, label: str, parent_id: str) -> ChangeReport:
        return self._add_element(f"add cause '{id}'", Cause(id, label), parent_id)
