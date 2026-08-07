from dataclasses import dataclass

from wireup import injectable

from ...runtime.diagrams.transaction import ChangeTransaction
from ..base import DiagramChanges
from .observer import FlowchartObserver


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class FlowchartChanges(DiagramChanges[ChangeTransaction, FlowchartObserver]):
    transaction: ChangeTransaction
    observer: FlowchartObserver
