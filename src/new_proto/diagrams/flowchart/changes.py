from dataclasses import dataclass

from wireup import injectable

from ..base import DiagramChanges
from .observer import FlowchartObserver
from .runtime import FlowchartTransaction


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class FlowchartChanges(DiagramChanges[FlowchartTransaction, FlowchartObserver]):
    transaction: FlowchartTransaction
    observer: FlowchartObserver
