from dataclasses import dataclass

from wireup import injectable

from ..base import DiagramChanges
from .observer import SequenceObserver
from .runtime import SequenceTransaction


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class SequenceChanges(DiagramChanges[SequenceTransaction, SequenceObserver]):
    transaction: SequenceTransaction
    observer: SequenceObserver
