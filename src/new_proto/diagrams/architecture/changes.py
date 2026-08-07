from dataclasses import dataclass

from wireup import injectable

from ..base import DiagramChanges
from .observer import ArchitectureObserver
from .runtime import ArchitectureTransaction


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class ArchitectureChanges(DiagramChanges[ArchitectureTransaction, ArchitectureObserver]):
    transaction: ArchitectureTransaction
    observer: ArchitectureObserver
