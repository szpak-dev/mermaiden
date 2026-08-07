from collections.abc import Sequence
from dataclasses import dataclass

from wireup import injectable

from ...runtime.diagrams.observer import ConstraintInspection
from ..base import DiagramObserver
from .constraints import SequenceConstraint


@injectable
@dataclass(frozen=True, slots=True)
class SequenceObserver(DiagramObserver[SequenceConstraint]):
    structure: ConstraintInspection
    constraints: Sequence[SequenceConstraint]
