"""Framework-free contracts and values for every diagram domain."""

from .annotation import Annotation, TargetKind, TargetRef
from .constraint import (
    ChangeRejected,
    ChangeReport,
    Constraint,
    ConstraintLevel,
    ValidationReport,
    Violation,
)
from .diagram import Diagram, DiagramVisitor
from .element import Container, Element, Entity
from .relation import Relation

__all__ = [
    "Annotation",
    "ChangeRejected",
    "ChangeReport",
    "Constraint",
    "ConstraintLevel",
    "Container",
    "Diagram",
    "DiagramVisitor",
    "Element",
    "Entity",
    "Relation",
    "TargetKind",
    "TargetRef",
    "ValidationReport",
    "Violation",
]
