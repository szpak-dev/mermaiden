from dataclasses import dataclass

from wireup import injectable

from ..base import DiagramChanges
from .observer import TreeViewObserver
from .runtime import TreeViewTransaction


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class TreeViewChanges(DiagramChanges[TreeViewTransaction, TreeViewObserver]):
    transaction: TreeViewTransaction
    observer: TreeViewObserver
