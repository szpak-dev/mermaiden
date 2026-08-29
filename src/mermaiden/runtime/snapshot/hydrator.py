from dataclasses import dataclass, fields
from typing import Any, cast

from wireup import injectable

from ...core.annotation import Annotation
from ...core.diagram import Diagram
from ...core.element import Element
from ...core.relation import Relation
from ..diagrams.state import DiagramData
from .configuration import DiagramConfigurationReader
from .domain import TRANSIENT_DIAGRAM_FIELDS, DiagramSnapshot, SnapshotError
from .value_decoder import SnapshotValueDecoder


@injectable
@dataclass(frozen=True, slots=True)
class DiagramSnapshotHydrator:
    values: SnapshotValueDecoder
    configurations: DiagramConfigurationReader

    def hydrate(self, snapshot: DiagramSnapshot, diagram: Diagram) -> DiagramData:
        current_configuration = self.configurations.read(diagram)
        configuration = self.values.decode(snapshot.configuration, type(current_configuration))
        if type(configuration) is not type(current_configuration):
            raise SnapshotError(f"Snapshot configuration is not valid for diagram '{diagram.kind}'.")
        object.__setattr__(diagram, "configuration", configuration)
        elements = tuple(self.values.decode(item, Element) for item in snapshot.elements)
        relations = tuple(self.values.decode(item, Relation) for item in snapshot.relations)
        annotations = tuple(self.values.decode(item, Annotation) for item in snapshot.annotations)
        for name, value in snapshot.properties.items():
            item = next((field for field in fields(cast(Any, diagram)) if field.name == name), None)
            if item is None or name in TRANSIENT_DIAGRAM_FIELDS:
                raise SnapshotError(f"Snapshot property '{name}' is not supported.")
            object.__setattr__(diagram, name, self.values.decode(value, item.type))
        return DiagramData(elements, relations, annotations)
