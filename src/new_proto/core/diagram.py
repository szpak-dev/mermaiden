from enum import StrEnum
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Protocol, TypeVar

from .annotation import Annotation
from .element import Element
from .relation import Relation

Result = TypeVar("Result", covariant=True)


class DiagramVisitor(Protocol[Result]):
    def visit(self, diagram: "Diagram") -> Result: ...


class Direction(StrEnum):
    TOP_DOWN = "TD"
    LEFT_RIGHT = "LR"
    RIGHT_LEFT = "RL"
    BOTTOM_UP = "BT"


class Diagram(ABC):
    """Read-only aggregate root for diagram state.

    Mutation deliberately does not appear in this contract.  Building is an
    application/runtime concern, while a completed diagram is a domain value.
    """

    @property
    @abstractmethod
    def id(self) -> str: ...

    @property
    @abstractmethod
    def elements(self) -> Sequence[Element]: ...

    @property
    @abstractmethod
    def relations(self) -> Sequence[Relation]: ...

    @property
    @abstractmethod
    def annotations(self) -> Sequence[Annotation]: ...

    @property
    @abstractmethod
    def constraints(self) -> Sequence["DiagramVisitor[object]"]: ...

    def accept(self, visitor: DiagramVisitor[Result]) -> Result:
        """Double-dispatch entry point used by constraints and renderers."""

        return visitor.visit(self)

