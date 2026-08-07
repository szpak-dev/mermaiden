from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Element(ABC):
    id: str
    label: str


@dataclass(frozen=True, slots=True)
class Entity(Element):
    pass


@dataclass(frozen=True, slots=True)
class Container(Element):
    elements: tuple[Element, ...] = ()
