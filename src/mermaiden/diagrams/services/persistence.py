from collections.abc import Mapping
from dataclasses import dataclass

from wireup import injectable

from ...runtime.snapshot import DiagramSnapshot, DiagramSnapshotCodec
from ..domain import DiagramModel
from .diagram_factory import DiagramFactory
from .persistence_validator import DiagramPersistenceValidator


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class DiagramPersistenceApplication:
    diagrams: DiagramFactory
    snapshots: DiagramSnapshotCodec
    validator: DiagramPersistenceValidator

    def snapshot(self, diagram: DiagramModel) -> DiagramSnapshot:
        self.validator.ensure(diagram, "persist")
        return self.snapshots.snapshot(diagram)

    def restore(self, payload: Mapping[str, object]) -> DiagramModel:
        snapshot = self.snapshots.restore(payload)
        diagram = self.diagrams.create(snapshot.kind)
        data = self.snapshots.hydrate(snapshot, diagram)
        diagram.restore_snapshot(data)
        self.validator.ensure(diagram, "restore")
        return diagram
