from new_proto.interface import Interface

from .annotation import Annotation
from .constraint import Constraint
from .query import DiagramQuery


class Diagram(DiagramQuery):
    @Interface.prop
    def annotations(self) -> tuple[Annotation, ...]: ...

    @Interface.prop
    def constraints(self) -> tuple[Constraint, ...]: ...
