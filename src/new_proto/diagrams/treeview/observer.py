from collections.abc import Sequence
from dataclasses import dataclass

from wireup import injectable

from ...runtime.diagrams.observer import ConstraintInspection
from ..base import DiagramObserver
from .constraints.constraint import TreeViewConstraint


@injectable
@dataclass(frozen=True, slots=True)
class TreeViewObserver(DiagramObserver[TreeViewConstraint]):
    structure: ConstraintInspection
    constraints: Sequence[TreeViewConstraint]
