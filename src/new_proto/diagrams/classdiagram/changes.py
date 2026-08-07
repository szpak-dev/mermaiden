from dataclasses import dataclass

from wireup import injectable

from ..base import DiagramChanges
from .observer import ClassDiagramObserver
from .runtime import ClassDiagramTransaction


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class ClassDiagramChanges(DiagramChanges[ClassDiagramTransaction, ClassDiagramObserver]):
    transaction: ClassDiagramTransaction
    observer: ClassDiagramObserver
