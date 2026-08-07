import re
from abc import ABC, abstractmethod

from ..core.constraint import BlockingConstraint, ValidationReport
from ..core.diagram import Diagram


class ConstraintInspection(ABC):
    @abstractmethod
    def inspect(self, diagram: Diagram) -> ValidationReport: ...


class StructureConstraint(BlockingConstraint):
    @property
    def code(self) -> str:
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", type(self).__name__).lower()
        return f"structure.{name}"
