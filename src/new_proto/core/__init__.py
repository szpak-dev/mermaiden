"""Stable, framework-free contracts for diagram domains."""

from .annotation import Annotation, TargetKind, TargetRef
from .constraint import Constraint, Severity, ValidationReport, Violation
from .diagram import Diagram, DiagramVisitor
from .element import Container, Element
from .relation import DirectedRelation, Relation

__all__ = [
    "Annotation",
    "Constraint",
    "Container",
    "Diagram",
    "DiagramVisitor",
    "DirectedRelation",
    "Element",
    "Relation",
    "Severity",
    "TargetKind",
    "TargetRef",
    "ValidationReport",
    "Violation",
]
