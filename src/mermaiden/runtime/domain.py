from abc import ABC, abstractmethod

from ..core.constraint import ValidationReport
from ..core.diagram import Diagram


class ConstraintInspection(ABC):
    @abstractmethod
    def inspect(self, diagram: Diagram) -> ValidationReport: ...
