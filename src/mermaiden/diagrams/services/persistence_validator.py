from dataclasses import dataclass

from wireup import injectable

from ...runtime.snapshot import SnapshotError
from ..domain import DiagramModel


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class DiagramPersistenceValidator:
    def ensure(self, diagram: DiagramModel, operation: str, *, allow_draft: bool = False) -> None:
        if allow_draft:
            return
        report = diagram.validate()
        if report.can_commit:
            return
        details = "; ".join(item.message for item in report.blocking)
        raise SnapshotError(f"Cannot {operation} invalid diagram '{diagram.kind}': {details}")
