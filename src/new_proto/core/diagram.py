from .annotation import Annotation
from .constraint import Constraint
from .query import DiagramQuery


class Diagram(DiagramQuery):
    annotations: tuple[Annotation, ...]
    constraints: tuple[Constraint, ...]
