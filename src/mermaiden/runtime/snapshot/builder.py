from collections.abc import Mapping
from dataclasses import dataclass, fields
from typing import Any, cast

from wireup import injectable

from ...core.domain import Diagram
from .configuration import DiagramConfigurationReader
from .domain import SNAPSHOT_VERSION, TRANSIENT_DIAGRAM_FIELDS, DiagramSnapshot
from .value_encoder import SnapshotValueEncoder


@injectable
@dataclass(frozen=True, slots=True)
class DiagramSnapshotBuilder:
    values: SnapshotValueEncoder
    configurations: DiagramConfigurationReader

    def build(self, diagram: Diagram) -> DiagramSnapshot:
        return DiagramSnapshot(
            version=SNAPSHOT_VERSION,
            kind=diagram.kind,
            configuration=cast(Mapping[str, object], self.values.encode(self.configurations.read(diagram))),
            elements=tuple(cast(Mapping[str, object], self.values.encode(item)) for item in diagram.root_elements),
            relations=tuple(cast(Mapping[str, object], self.values.encode(item)) for item in diagram.find_relations()),
            annotations=tuple(
                cast(Mapping[str, object], self.values.encode(item)) for item in diagram.find_annotations()
            ),
            properties={
                item.name: self.values.encode(getattr(diagram, item.name))
                for item in fields(cast(Any, diagram))
                if item.name not in TRANSIENT_DIAGRAM_FIELDS
            },
        )
