from collections.abc import Sequence
from dataclasses import dataclass

from wireup import injectable

from ...runtime.diagrams.observer import ConstraintInspection
from ..base import DiagramObserver
from .constraints import ClassDiagramConstraint


@injectable
@dataclass(frozen=True, slots=True)
class ClassDiagramObserver(DiagramObserver[ClassDiagramConstraint]):
    structure: ConstraintInspection
    constraints: Sequence[ClassDiagramConstraint]
