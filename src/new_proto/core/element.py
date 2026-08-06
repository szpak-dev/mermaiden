from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Element(ABC):
    """A named building block whose identity is local to one diagram."""

    id: str
    label: str


@dataclass(frozen=True, slots=True)
class Entity(Element):
    """An element representing one singular thing."""


@dataclass(frozen=True, slots=True)
class Container(Element):
    """An element containing other elements recursively."""

    elements: tuple[Element, ...] = ()
