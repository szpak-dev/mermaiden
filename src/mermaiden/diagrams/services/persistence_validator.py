from dataclasses import dataclass

from wireup import injectable

from ...runtime.snapshot import SnapshotError
from ..domain import DiagramModel


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class DiagramPersistenceValidator:
    def ensure(self, diagram: DiagramModel, operation: str) -> None:
        report = diagram.validate()
        if report.can_commit:
            return
        details = "; ".join(item.message for item in report.blocking)
        raise SnapshotError(f"Cannot {operation} invalid diagram '{diagram.kind}': {details}")
