from collections.abc import Mapping
from dataclasses import dataclass

from wireup import injectable

from ...core.domain import ChangeReport
from ...runtime.snapshot import DiagramSnapshot, DiagramSnapshotCodec, SnapshotError
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
        return self.snapshots.snapshot(diagram)

    def restore(self, payload: Mapping[str, object]) -> DiagramModel:
        snapshot = self.snapshots.restore(payload)
        diagram = self.diagrams.create(snapshot.kind)
        self.restore_into(diagram, snapshot)
        return diagram

    def restore_into(self, diagram: DiagramModel, snapshot: DiagramSnapshot) -> ChangeReport:
        before = self.snapshots.snapshot(diagram)
        try:
            return self._restore_into(diagram, snapshot)
        except Exception:
            self._restore_into(diagram, before)
            raise

    def _restore_into(self, diagram: DiagramModel, snapshot: DiagramSnapshot) -> ChangeReport:
        if snapshot.kind != diagram.kind:
            raise SnapshotError(f"Snapshot kind '{snapshot.kind}' does not match diagram kind '{diagram.kind}'.")
        data = self.snapshots.hydrate(snapshot, diagram)
        report = diagram.restore_snapshot(data)
        self.validator.ensure(diagram, "restore", allow_draft=snapshot.draft)
        return report
