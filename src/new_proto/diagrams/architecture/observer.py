from collections.abc import Sequence
from dataclasses import dataclass

from wireup import injectable

from ...runtime.diagrams.observer import ConstraintInspection
from ..base import DiagramObserver
from .constraints import ArchitectureConstraint


@injectable
@dataclass(frozen=True, slots=True)
class ArchitectureObserver(DiagramObserver[ArchitectureConstraint]):
    structure: ConstraintInspection
    constraints: Sequence[ArchitectureConstraint]
