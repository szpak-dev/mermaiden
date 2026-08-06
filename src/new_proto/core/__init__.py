"""Framework-free contracts and values for every diagram domain."""

from .annotation import Annotation, DataAnnotation, TargetKind, TargetRef
from .constraint import (
    ChangeRejected,
    ChangeReport,
    Constraint,
    ConstraintLevel,
    ValidationReport,
    Violation,
)
from .diagram import Diagram, DiagramView, DiagramVisitor
from .element import Container, Element, Entity
from .error import OperationError
from .relation import Relation
from .rendering import Renderer

__all__ = [
    "Annotation",
    "ChangeRejected",
    "ChangeReport",
    "Constraint",
    "ConstraintLevel",
    "Container",
    "DataAnnotation",
    "Diagram",
    "DiagramView",
    "DiagramVisitor",
    "Element",
    "Entity",
    "OperationError",
    "Relation",
    "Renderer",
    "TargetKind",
    "TargetRef",
    "ValidationReport",
    "Violation",
]
