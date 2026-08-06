from new_proto.interface import Interface

from .annotation import Annotation
from .constraint import Constraint
from .query import DiagramQuery


class Diagram(DiagramQuery):
    """The complete context of elements, relations, constraints, and annotations.

    Elements form the full membership of the diagram. Relations are known by the
    diagram but remain outside the containment tree owned by containers.
    """

    @Interface.prop
    def annotations(self) -> tuple[Annotation, ...]: ...

    @Interface.prop
    def constraints(self) -> tuple[Constraint, ...]: ...
